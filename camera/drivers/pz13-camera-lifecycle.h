/* SPDX-License-Identifier: GPL-2.0 */
/* Shared lifecycle for the staged PZ13 sensor candidates, not an autoload driver.
 * stream_lock serializes stream transitions; lock protects controls and power.
 * The worker takes only lock. Never wait for the worker while holding lock.
 */
static void latch_fault(int error)
{
	if (error && !faulted) {
		stream_result = error;
		faulted = true;
	}
}

static void stop_locked(struct pz13_capture *f)
{
	int ret;
	if (!f->streaming)
		return;
	latch_fault(write_reg(f, 0x0100, 0, 1));
	f->streaming = false;
	ret = pm_runtime_put_sync(&f->client->dev);
	if (ret < 0)
		latch_fault(ret);
	latch_fault(cleanup_error);
	stream_stops++;
}

static void deadline_work(struct work_struct *work)
{
	struct pz13_capture *f = container_of(to_delayed_work(work),
					    struct pz13_capture, deadline);
	mutex_lock(&f->lock);
	if (f->streaming) {
		latch_fault(-ETIMEDOUT);
		stop_locked(f);
		dev_warn(&f->client->dev, "PZ13 lifecycle: fault/deadline stop %d\n",
			 stream_result);
	}
	mutex_unlock(&f->lock);
}

static int set_stream(struct v4l2_subdev *sd, int enable)
{
	struct pz13_capture *f = from_sd(sd);
	struct device *dev = &f->client->dev;
	int ret = 0, pmret;

	mutex_lock(&f->stream_lock);
	if (!enable) {
		cancel_delayed_work_sync(&f->deadline);
		mutex_lock(&f->lock);
		stop_locked(f);
		ret = faulted ? stream_result : 0;
		goto out;
	}
	mutex_lock(&f->lock);
	if (f->removing || faulted || cleanup_error) {
		ret = -EIO;
		goto out;
	}
	if (f->streaming)
		goto out;
	if (max_starts && stream_starts >= max_starts) {
		ret = -EOVERFLOW;
		goto out;
	}
	/* A successful prior stop synchronously drained its timer. A timer-driven
	 * stop latches faulted and cannot reach here, even if work is still ending.
	 */
	attempted = true;
	stream_starts++;
	ret = pm_runtime_resume_and_get(dev);
	if (ret < 0)
		goto result;
	ret = initialize_stream(f);
	if (ret) {
		latch_fault(ret);
		latch_fault(write_reg(f, 0x0100, 0, 1));
		pmret = pm_runtime_put_sync(dev);
		if (pmret < 0)
			latch_fault(pmret);
		latch_fault(cleanup_error);
	} else {
		f->streaming = true;
		if (stream_timeout_ms)
			schedule_delayed_work(&f->deadline,
					      msecs_to_jiffies(stream_timeout_ms));
	}
result:
	if (ret)
		latch_fault(ret);
	else
		stream_result = 0;
	dev_info(dev, "PZ13 lifecycle: start=%u result=%d\n", stream_starts, ret);
out:
	mutex_unlock(&f->lock);
	mutex_unlock(&f->stream_lock);
	return ret;
}

/* Idle sleep is supported. Refuse active sleep until the application has
 * stopped the stream: silently removing sensor power loses the CSI contract.
 */
static int system_suspend(struct device *dev)
{
	struct pz13_capture *f = from_sd(dev_get_drvdata(dev));
	int ret;
	mutex_lock(&f->stream_lock);
	mutex_lock(&f->lock);
	ret = f->streaming ? -EBUSY : cleanup_error;
	mutex_unlock(&f->lock);
	if (!ret)
		ret = pm_runtime_force_suspend(dev);
	mutex_unlock(&f->stream_lock);
	return ret;
}
