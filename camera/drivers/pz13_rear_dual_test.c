// SPDX-License-Identifier: GPL-2.0
/* Manual PZ13 rear software-ISP experiment. Tables remain owner-private. */
#include <linux/clk.h>
#include <linux/delay.h>
#include <linux/gpio/consumer.h>
#include <linux/i2c.h>
#include <linux/module.h>
#include <linux/of.h>
#include <linux/pinctrl/consumer.h>
#include <linux/pm_runtime.h>
#include <linux/regulator/consumer.h>
#include <linux/unaligned.h>
#include <linux/workqueue.h>
#include <media/v4l2-ctrls.h>
#include <media/v4l2-device.h>
#include <media/v4l2-fwnode.h>

static bool reviewed, validate_only, registered, attempted, powered_down = true;
static int stream_result = -EINPROGRESS, cleanup_error;
static bool faulted;
static unsigned int stream_starts, stream_stops;
static unsigned int stream_timeout_ms = 15000, max_starts = 32;
module_param(faulted, bool, 0400);
module_param(stream_starts, uint, 0400);
module_param(stream_stops, uint, 0400);
module_param(stream_timeout_ms, uint, 0400);
module_param(max_starts, uint, 0400);
static void latch_fault(int error);
static bool lens_attempted;
static int lens_result = -EINPROGRESS, lens_park_result = -EINPROGRESS;
module_param(lens_attempted, bool, 0400);
module_param(lens_result, int, 0400);
module_param(lens_park_result, int, 0400);
module_param(reviewed, bool, 0400);
module_param(validate_only, bool, 0400);
module_param(attempted, bool, 0400);
module_param(powered_down, bool, 0400);
module_param(stream_result, int, 0400);
module_param(cleanup_error, int, 0400);





struct rail_spec {
 const char *name, *path, *compatible, *pmic, *supply, *child;
 u32 parent, phandle, voltage;
};
/* Exact external module D0 enable order from the selected ASUS resource. */
static const struct rail_spec rails[] = {
 { "b7", "/soc@0/rsc@17500000/pz13-rear-pm8550", "qcom,pm8550-rpmh-regulators", "b", "vdd-l6-l7-supply", "ldo7", 0x189, 0x1d2, 2800000 },
 { "m6", "/soc@0/rsc@17500000/pz13-rear-pm8010", "qcom,pm8010-rpmh-regulators", "m", "vdd-l6-supply", "ldo6", 0x187, 0x1d0, 1800000 },
 { "m2", "/soc@0/rsc@17500000/pz13-rear-pm8010", "qcom,pm8010-rpmh-regulators", "m", "vdd-l1-l2-supply", "ldo2", 0x18a, 0x1cd, 1200000 },
 { "m4", "/soc@0/rsc@17500000/pz13-rear-pm8010", "qcom,pm8010-rpmh-regulators", "m", "vdd-l3-l4-supply", "ldo4", 0x187, 0x1ce, 1800000 },
 { "m5", "/soc@0/rsc@17500000/pz13-rear-pm8010", "qcom,pm8010-rpmh-regulators", "m", "vdd-l5-supply", "ldo5", 0x188, 0x1cf, 2800000 },
 { "b5", "/soc@0/rsc@17500000/pz13-rear-pm8550", "qcom,pm8550-rpmh-regulators", "b", "vdd-l5-l16-supply", "ldo5", 0x188, 0x1d1, 3000000 },
};
#include "pz13-dual-tree-guard.h"

static int validate_board(void)
{
	return reviewed ? pz13_validate_dual_tree() : -EPERM;
}

static int validate_endpoints(void)
{
	/* Included in the exact combined-tree validation above. */
	return 0;
}

struct pz13_reg { u16 address; u8 value; };
/* Only the explicitly reviewed 24 MHz full-resolution tables, never firmware. */
#include "pz13-rear-24mhz-private.h"

#define PZ13_WIDTH 4224
#define PZ13_HEIGHT 3136
#define PZ13_VTS 3214
#define PZ13_LINE_PIXELS 4488
#define PZ13_PIXEL_RATE 432000000LL
#define PZ13_LINK_FREQ 540000000LL
#define PZ13_CODE MEDIA_BUS_FMT_SBGGR10_1X10

struct rear_capture {
	struct i2c_client *client;
	struct v4l2_subdev sd;
	struct media_pad pad;
	struct v4l2_ctrl_handler controls;
	struct mutex lock, stream_lock;
	bool removing;
	struct delayed_work deadline;
	struct regulator *regulators[ARRAY_SIZE(rails)];
	struct gpio_desc *reset;
	struct pinctrl *pins;
	struct pinctrl_state *active, *sleep;
	struct clk *mclk;
	bool on[ARRAY_SIZE(rails)], clock_on, powered, streaming;
	bool lens_identified, lens_active;
	unsigned int lens_code;
};

static struct rear_capture *from_sd(struct v4l2_subdev *sd)
{
	return container_of(sd, struct rear_capture, sd);
}

static int write_reg(struct rear_capture *f, u16 reg, u32 value, u8 size)
{
	u8 data[5];
	int ret;
	if (!size || size > 3)
		return -EINVAL;
	put_unaligned_be16(reg, data);
	for (int i = 0; i < size; i++)
		data[2 + i] = value >> (8 * (size - i - 1));
	ret = i2c_master_send(f->client, data, size + 2);
	return ret == size + 2 ? 0 : ret < 0 ? ret : -EIO;
}

static int read_id(struct rear_capture *f)
{
	u8 address[] = {0x30, 0x0a}, data[3];
	struct i2c_msg messages[] = {
		{ .addr = 0x36, .len = 2, .buf = address },
		{ .addr = 0x36, .flags = I2C_M_RD, .len = 3, .buf = data },
	};
	int ret = i2c_transfer(f->client->adapter, messages, 2);
	if (ret != 2)
		return ret < 0 ? ret : -EIO;
	return get_unaligned_be24(data) == 0x00d855 ? 0 : -ENODEV;
}

#include "pz13-rear-lens-private.h"
/* Caller holds the sensor control lock; power callbacks run under it. */
static int lens_write(struct rear_capture *f, u8 reg, u8 value)
{
 u8 data[] = { reg, value };
 struct i2c_msg m = { .addr = 0x0c, .len = 2, .buf = data };
 int ret = i2c_transfer(f->client->adapter, &m, 1);
 return ret == 1 ? 0 : ret < 0 ? ret : -EIO;
}

static int lens_read(struct rear_capture *f, u8 reg, u8 *value)
{
 struct i2c_msg m[] = {
  { .addr = 0x0c, .len = 1, .buf = &reg },
  { .addr = 0x0c, .flags = I2C_M_RD, .len = 1, .buf = value },
 };
 int ret = i2c_transfer(f->client->adapter, m, 2);
 return ret == 2 ? 0 : ret < 0 ? ret : -EIO;
}

static int lens_idle(struct rear_capture *f)
{
 u8 status;
 int ret;
 for (int i = 0; i < 50; i++) {
  ret = lens_read(f, 0x05, &status);
  if (ret) return ret;
  if (!(status & 1)) return 0;
  usleep_range(2000, 2200);
 }
 return -ETIMEDOUT;
}

static int lens_dac(struct rear_capture *f, unsigned int code)
{
 u8 data[] = { 0x03, code >> 8, code & 0xff }, hi, lo;
 struct i2c_msg m = { .addr = 0x0c, .len = 3, .buf = data };
 int ret;
 if (!f->lens_active || code > PZ13_LENS_MAX)
  return -EPERM;
 ret = lens_idle(f);
 if (ret) return ret;
 ret = i2c_transfer(f->client->adapter, &m, 1);
 if (ret != 1) return ret < 0 ? ret : -EIO;
 ret = lens_idle(f);
 if (!ret) ret = lens_read(f, 0x03, &hi);
 if (!ret) ret = lens_read(f, 0x04, &lo);
 if (!ret && (((hi & 3) << 8) | lo) != code) ret = -EIO;
 if (!ret) f->lens_code = code;
 return ret;
}

static int lens_position(struct rear_capture *f, unsigned int code)
{
 int ret;
 if (code < PZ13_LENS_MIN || code > PZ13_LENS_MAX)
  return -ERANGE;
 if (lens_result) return -EPERM;
 ret = lens_dac(f, code);
 if (ret) lens_result = ret;
 dev_info(&f->client->dev, "PZ13 FOCUS: requested=%u readback=%u result=%d\n", code, f->lens_code, ret);
 return ret;
}

static int lens_initialize(struct rear_capture *f)
{
 u8 id, revision, value;
 int ret;
 if (!f->powered || f->lens_active || faulted) return -EPERM;
 lens_attempted = true;
 usleep_range(1000, 1200);
 ret = lens_write(f, 0xed, 0xab);
 if (!ret) ret = lens_read(f, 0x00, &id);
 if (!ret && id != 0xfe) ret = -ENODEV;
 if (ret) goto fail;
 f->lens_identified = true;
 ret = lens_read(f, 0x01, &revision);
 if (ret) goto fail;
 dev_info(&f->client->dev, "PZ13 FOCUS: IC=0x%02x revision=0x%02x\n", id, revision);
 /* Exact owned module initialization, reviewed against manufacturer protocol. */
 for (unsigned int i = 1; i < ARRAY_SIZE(pz13_lens_init); i++) {
  ret = lens_write(f, pz13_lens_init[i][0], pz13_lens_init[i][1]);
  if (ret) goto fail;
  if (pz13_lens_init[i][0] == 2 && pz13_lens_init[i][1] == 0) {
   f->lens_active = true;
   usleep_range(1000, 1200);
  }
  ret = lens_read(f, pz13_lens_init[i][0], &value);
  if (!ret && value != pz13_lens_init[i][1]) ret = -EIO;
  if (ret) goto fail;
 }
 lens_result = 0;
 return 0;
fail:
 lens_result = ret;
 return ret;
}

static int lens_park(struct rear_capture *f)
{
 int ret = 0, pdret;
 u8 pd;
 if (!f->lens_identified) return 0;
 if (f->lens_active) {
  /* Small downward steps from the last verified position; never increase. */
  while (f->lens_code && !ret) {
   unsigned int next = f->lens_code > 16 ? f->lens_code - 16 : 0;
   ret = lens_dac(f, next);
   if (!ret) usleep_range(2000, 2200);
  }
 }
 pdret = lens_write(f, 0x02, 1);
 if (!pdret) pdret = lens_read(f, 0x02, &pd);
 if (!pdret && pd != 1) pdret = -EIO;
 if (!ret) ret = pdret;
 f->lens_active = false;
 lens_park_result = ret;
 dev_info(&f->client->dev, "PZ13 FOCUS: parked=%u power_down_result=%d result=%d\n", f->lens_code, pdret, ret);
 return ret;
}

static void remember_cleanup(int error)
{
	if (error && !cleanup_error)
		cleanup_error = error;
}

static int power_off(struct device *dev)
{
 struct rear_capture *f = from_sd(dev_get_drvdata(dev));
 const unsigned int order[] = {0, 2, 4, 1, 3, 5};
 unsigned int i, index;
 int ret;
 if (f->powered) remember_cleanup(lens_park(f));
 f->lens_identified = false;
 remember_cleanup(gpiod_set_value_cansleep(f->reset, 0));
 usleep_range(1000, 1200);
 if (f->clock_on) {
  clk_disable_unprepare(f->mclk);
  f->clock_on = false;
 }
 for (i = 0; i < ARRAY_SIZE(order); i++) {
  index = order[i];
  if (f->on[index]) {
   ret = regulator_disable(f->regulators[index]);
   remember_cleanup(ret);
   if (!ret) f->on[index] = false;
  }
 }
 remember_cleanup(pinctrl_select_state(f->pins, f->sleep));
 f->powered = false;
 powered_down = !cleanup_error && !f->clock_on;
 for (i = 0; i < ARRAY_SIZE(rails); i++)
  powered_down = powered_down && !f->on[i];
 dev_info(dev, "PZ13 REAR ISP: shutdown, cleanup=%d powered_down=%d\n", cleanup_error, powered_down);
 return cleanup_error;
}

static int power_on(struct device *dev)
{
 struct rear_capture *f = from_sd(dev_get_drvdata(dev));
 unsigned int i;
 int ret;
 powered_down = false;
 ret = pinctrl_select_state(f->pins, f->active);
 if (!ret) ret = gpiod_set_value_cansleep(f->reset, 0);
 if (ret) goto fail;
 for (i = 0; i < ARRAY_SIZE(rails); i++) {
  ret = regulator_set_voltage(f->regulators[i], rails[i].voltage, rails[i].voltage);
  if (!ret) ret = regulator_set_mode(f->regulators[i], REGULATOR_MODE_NORMAL);
  if (ret) goto fail;
 }
 ret = clk_set_rate(f->mclk, 24000000);
 if (!ret && clk_get_rate(f->mclk) != 24000000) ret = -EINVAL;
 if (ret) goto fail;
 for (i = 0; i < ARRAY_SIZE(rails); i++) {
  ret = regulator_enable(f->regulators[i]);
  if (ret) goto fail;
  f->on[i] = true;
  dev_info(dev, "PZ13 REAR ISP: %s enabled at %u uV\n", rails[i].name, rails[i].voltage);
  if (!i) usleep_range(1000, 1200);
 }
 ret = clk_prepare_enable(f->mclk);
 if (ret) goto fail;
 f->clock_on = true;
 usleep_range(5000, 5200);
 ret = gpiod_set_value_cansleep(f->reset, 1);
 if (ret) goto fail;
 usleep_range(1000, 1200);
 f->powered = true;
 dev_info(dev, "PZ13 REAR ISP: proven six-rail sequence, MCLK0 24 MHz\n");
 return 0;
fail:
 power_off(dev);
 return ret;
}

static int write_table(struct rear_capture *f, const struct pz13_reg *table,
		       size_t count)
{
	int ret;
	for (size_t i = 0; i < count; i++) {
		ret = write_reg(f, table[i].address, table[i].value, 1);
		if (ret)
			return ret;
		/* Do not issue the next write while software reset is settling. */
		if (table[i].address == 0x0103)
			usleep_range(2000, 2200);
	}
	return 0;
}

static int apply_control(struct v4l2_ctrl *ctrl)
{
	struct rear_capture *f = container_of(ctrl->handler,
					      struct rear_capture, controls);
	if (!f->powered)
		return 0;
	switch (ctrl->id) {
	case V4L2_CID_FOCUS_ABSOLUTE:
		return lens_position(f, ctrl->val);
	case V4L2_CID_EXPOSURE:
		/* Same exposure units as the upstream OV13858 driver. */
		return write_reg(f, 0x3500, ctrl->val << 4, 3);
	case V4L2_CID_ANALOGUE_GAIN:
		return write_reg(f, 0x3508, ctrl->val, 2);
	default:
		return -EINVAL;
	}
}

static int set_control(struct v4l2_ctrl *ctrl)
{
 struct rear_capture *f = container_of(ctrl->handler, struct rear_capture, controls);
 int ret;
 if (faulted) return -EIO;
 ret = apply_control(ctrl);
 if (ret) {
  latch_fault(ret);
  if (f->streaming) mod_delayed_work(system_wq, &f->deadline, 0);
 }
 return ret;
}

static const struct v4l2_ctrl_ops control_ops = { .s_ctrl = set_control };
static const s64 frequencies[] = { PZ13_LINK_FREQ };

/* Caller holds f->lock; runtime callbacks deliberately do not acquire it. */




static int initialize_stream(struct rear_capture *f)
{
 int ret;
	ret = read_id(f);
	if (!ret)
		ret = lens_initialize(f);
	if (!ret)
		ret = write_table(f, pz13_rear_full, ARRAY_SIZE(pz13_rear_full));
	if (!ret)
		ret = __v4l2_ctrl_handler_setup(&f->controls);
	if (!ret)
		ret = write_reg(f, 0x0100, 1, 1);
 return ret;
}
#define pz13_capture rear_capture
#include "pz13-camera-lifecycle.h"
#undef pz13_capture

static void fill_format(struct v4l2_mbus_framefmt *fmt)
{
	*fmt = (struct v4l2_mbus_framefmt) {
		.width = PZ13_WIDTH, .height = PZ13_HEIGHT, .code = PZ13_CODE,
		.field = V4L2_FIELD_NONE, .colorspace = V4L2_COLORSPACE_RAW,
	};
}

static int get_format(struct v4l2_subdev *sd, struct v4l2_subdev_state *state,
		      struct v4l2_subdev_format *fmt)
{
	if (fmt->pad)
		return -EINVAL;
	fill_format(&fmt->format);
	return 0;
}

static int set_format(struct v4l2_subdev *sd, struct v4l2_subdev_state *state,
		      struct v4l2_subdev_format *fmt)
{
	int ret = get_format(sd, state, fmt);
	if (!ret && fmt->which == V4L2_SUBDEV_FORMAT_TRY)
		*v4l2_subdev_state_get_format(state, 0) = fmt->format;
	return ret;
}

static int enum_code(struct v4l2_subdev *sd, struct v4l2_subdev_state *state,
		     struct v4l2_subdev_mbus_code_enum *code)
{
	if (code->pad || code->index)
		return -EINVAL;
	code->code = PZ13_CODE;
	return 0;
}

static int enum_size(struct v4l2_subdev *sd, struct v4l2_subdev_state *state,
		     struct v4l2_subdev_frame_size_enum *size)
{
	if (size->pad || size->index || size->code != PZ13_CODE)
		return -EINVAL;
	size->min_width = size->max_width = PZ13_WIDTH;
	size->min_height = size->max_height = PZ13_HEIGHT;
	return 0;
}

static int open_subdev(struct v4l2_subdev *sd, struct v4l2_subdev_fh *fh)
{
	fill_format(v4l2_subdev_state_get_format(fh->state, 0));
	return 0;
}

static const struct v4l2_subdev_internal_ops internal_ops = { .open = open_subdev };
static const struct media_entity_operations entity_ops = {
	.link_validate = v4l2_subdev_link_validate,
};
static const struct v4l2_subdev_video_ops video_ops = { .s_stream = set_stream };
static const struct v4l2_subdev_pad_ops pad_ops = {
	.set_fmt = set_format, .get_fmt = get_format,
	.enum_mbus_code = enum_code, .enum_frame_size = enum_size,
};
static const struct v4l2_subdev_ops subdev_ops = {
	.video = &video_ops, .pad = &pad_ops,
};

static int capture_probe(struct i2c_client *client)
{
	struct device *dev = &client->dev;
	struct rear_capture *f;
	struct v4l2_ctrl *ctrl;
	struct device_node *expected;
	int ret;
	expected = of_find_node_by_path("/soc@0/cci@ac15000/i2c-bus@0/camera@36");
	ret = client->addr == 0x36 && dev->of_node == expected ? 0 : -EINVAL;
	of_node_put(expected);
	if (ret)
		return ret;
	f = devm_kzalloc(dev, sizeof(*f), GFP_KERNEL);
	if (!f)
		return -ENOMEM;
	f->client = client;
 for (unsigned int i = 0; i < ARRAY_SIZE(rails); i++) {
  f->regulators[i] = devm_regulator_get(dev, rails[i].name);
  if (IS_ERR(f->regulators[i])) return PTR_ERR(f->regulators[i]);
 }
 f->mclk = devm_clk_get(dev, "mclk");
 f->pins = devm_pinctrl_get(dev);
 if (IS_ERR(f->mclk) || IS_ERR(f->pins)) return -ENODEV;
	f->active = pinctrl_lookup_state(f->pins, "default");
	f->sleep = pinctrl_lookup_state(f->pins, "sleep");
	if (IS_ERR(f->active) || IS_ERR(f->sleep))
		return -EINVAL;
	f->reset = devm_gpiod_get(dev, "reset-line", GPIOD_OUT_LOW);
	if (IS_ERR(f->reset))
		return -ENODEV;
	ret = pinctrl_select_state(f->pins, f->sleep);
	if (ret)
		return ret;
	mutex_init(&f->lock);
	mutex_init(&f->stream_lock);
	INIT_DELAYED_WORK(&f->deadline, deadline_work);
	v4l2_i2c_subdev_init(&f->sd, client, &subdev_ops);
	/* Verified physical model selects libcamera's OV13858 gain helper. */
	snprintf(f->sd.name, sizeof(f->sd.name), "ov13858 %d-%04x",
		 i2c_adapter_id(client->adapter), client->addr);
	f->sd.internal_ops = &internal_ops;
	f->sd.flags |= V4L2_SUBDEV_FL_HAS_DEVNODE;
	f->sd.entity.ops = &entity_ops;
	f->sd.entity.function = MEDIA_ENT_F_CAM_SENSOR;
	f->pad.flags = MEDIA_PAD_FL_SOURCE;
	v4l2_ctrl_handler_init(&f->controls, 8);
	f->controls.lock = &f->lock;
	ctrl = v4l2_ctrl_new_int_menu(&f->controls, NULL, V4L2_CID_LINK_FREQ,
				    0, 0, frequencies);
	if (ctrl)
		ctrl->flags |= V4L2_CTRL_FLAG_READ_ONLY;
	ctrl = v4l2_ctrl_new_std(&f->controls, NULL, V4L2_CID_PIXEL_RATE,
			       PZ13_PIXEL_RATE, PZ13_PIXEL_RATE, 1, PZ13_PIXEL_RATE);
	if (ctrl)
		ctrl->flags |= V4L2_CTRL_FLAG_READ_ONLY;
	ctrl = v4l2_ctrl_new_std(&f->controls, NULL, V4L2_CID_HBLANK,
			       PZ13_LINE_PIXELS - PZ13_WIDTH,
			       PZ13_LINE_PIXELS - PZ13_WIDTH, 1,
			       PZ13_LINE_PIXELS - PZ13_WIDTH);
	if (ctrl)
		ctrl->flags |= V4L2_CTRL_FLAG_READ_ONLY;
	ctrl = v4l2_ctrl_new_std(&f->controls, NULL, V4L2_CID_VBLANK,
			       PZ13_VTS - PZ13_HEIGHT, PZ13_VTS - PZ13_HEIGHT,
			       1, PZ13_VTS - PZ13_HEIGHT);
	if (ctrl)
		ctrl->flags |= V4L2_CTRL_FLAG_READ_ONLY;
	v4l2_ctrl_new_std(&f->controls, &control_ops, V4L2_CID_EXPOSURE,
			 4, PZ13_VTS - 8, 1, 1600);
	v4l2_ctrl_new_std(&f->controls, &control_ops, V4L2_CID_ANALOGUE_GAIN,
			 128, 2047, 1, 128);
	v4l2_ctrl_new_std(&f->controls, &control_ops, V4L2_CID_FOCUS_ABSOLUTE,
		 PZ13_LENS_MIN, PZ13_LENS_MAX, 1, PZ13_LENS_MIN);
	/* This variant is board-specific: the verified sensor is rear-facing. */
	ctrl = v4l2_ctrl_new_std_menu(&f->controls, NULL,
			V4L2_CID_CAMERA_ORIENTATION, V4L2_CAMERA_ORIENTATION_EXTERNAL,
			0, V4L2_CAMERA_ORIENTATION_BACK);
	if (ctrl)
		ctrl->flags |= V4L2_CTRL_FLAG_READ_ONLY;
	f->sd.ctrl_handler = &f->controls;
	ret = f->controls.error;
	if (ret)
		goto free_controls;
	ret = media_entity_pads_init(&f->sd.entity, 1, &f->pad);
	if (ret)
		goto free_controls;
	pm_runtime_set_suspended(dev);
	pm_runtime_enable(dev);
	ret = v4l2_async_register_subdev_sensor(&f->sd);
	if (ret)
		goto free_entity;
	dev_info(dev, "PZ13 REAR ISP: registered, sensor rails remain off\n");
	return 0;
free_entity:
	pm_runtime_disable(dev);
	media_entity_cleanup(&f->sd.entity);
free_controls:
	v4l2_ctrl_handler_free(&f->controls);
	mutex_destroy(&f->stream_lock);
	mutex_destroy(&f->lock);
	return ret;
}

static void capture_remove(struct i2c_client *client)
{
	struct v4l2_subdev *sd = i2c_get_clientdata(client);
	struct rear_capture *f = from_sd(sd);
	v4l2_async_unregister_subdev(sd);
	mutex_lock(&f->stream_lock);
	f->removing = true;
	cancel_delayed_work_sync(&f->deadline);
	mutex_lock(&f->lock);
	stop_locked(f);
	mutex_unlock(&f->lock);
	mutex_unlock(&f->stream_lock);
	pm_runtime_disable(&client->dev);
	media_entity_cleanup(&sd->entity);
	v4l2_ctrl_handler_free(&f->controls);
	mutex_destroy(&f->stream_lock);
	mutex_destroy(&f->lock);
}

static const struct dev_pm_ops capture_pm = {
	SET_RUNTIME_PM_OPS(power_off, power_on, NULL)
	SET_SYSTEM_SLEEP_PM_OPS(system_suspend, pm_runtime_force_resume)
};
static const struct of_device_id capture_match[] = {
	{ .compatible = "pz13,rear-capture-test" }, {}
};
static struct i2c_driver capture_driver = {
	.driver = { .name = "pz13-rear-capture-test", .pm = &capture_pm,
		    .of_match_table = capture_match },
	.probe = capture_probe, .remove = capture_remove,
};

static int __init capture_init(void)
{
	int ret;
	if ((stream_timeout_ms && stream_timeout_ms < 1000) ||
	    stream_timeout_ms > 1800000 || max_starts > 64) return -EINVAL;
	ret = validate_board();
	if (!ret)
		ret = validate_endpoints();
	if (ret)
		return ret;
	if (validate_only) {
		pr_info("PZ13 REAR ISP: validation only; no registration or power\n");
		return 0;
	}
	ret = i2c_add_driver(&capture_driver);
	registered = !ret;
	return ret;
}
static void __exit capture_exit(void)
{
	if (registered)
		i2c_del_driver(&capture_driver);
}
module_init(capture_init);
module_exit(capture_exit);
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("PZ13 staged repeatable rear capture, synchronized deadline and fault latch");
