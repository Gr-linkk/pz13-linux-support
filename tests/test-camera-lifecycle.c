/* SPDX-License-Identifier: GPL-2.0 */
/* Execute the actual shared lifecycle with fake I/O and real pthread locks. */
#include <assert.h>
#include <errno.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>
#include <pthread.h>
#include <string.h>

struct mutex { pthread_mutex_t native; };
static void mutex_lock(struct mutex *m) { assert(!pthread_mutex_lock(&m->native)); }
static void mutex_unlock(struct mutex *m) { assert(!pthread_mutex_unlock(&m->native)); }
struct work_struct { int unused; };
struct delayed_work { struct work_struct work; bool pending, running; pthread_t worker; };
struct device { int refs; };
struct client { struct device dev; };
struct v4l2_subdev { int unused; };
struct pz13_capture {
 struct client *client;
 struct mutex lock, stream_lock;
 struct delayed_work deadline;
 struct v4l2_subdev sd;
 bool streaming, removing;
};
static bool faulted, attempted;
static int stream_result, cleanup_error, fail_init, fail_write, fail_resume, fail_put;
static unsigned int stream_starts, stream_stops, max_starts=3, stream_timeout_ms=15000;
static struct pz13_capture *current;
#define container_of(p,t,m) ((t *)((char *)(p)-offsetof(t,m)))
#define to_delayed_work(w) container_of(w,struct delayed_work,work)
#define dev_info(...) ((void)0)
#define dev_warn(...) ((void)0)
#define msecs_to_jiffies(x) (x)
static struct pz13_capture *from_sd(struct v4l2_subdev *sd) { return container_of(sd,struct pz13_capture,sd); }
static struct v4l2_subdev *dev_get_drvdata(struct device *d) { (void)d; return &current->sd; }
static int write_reg(struct pz13_capture *f,int a,int v,int n) { (void)f;(void)a;(void)v;(void)n;return fail_write; }
static int pm_runtime_resume_and_get(struct device *d) { if(fail_resume)return fail_resume;return d->refs++,0; }
static int pm_runtime_put_sync(struct device *d) { assert(d->refs==1);d->refs--;return fail_put; }
static int initialize_stream(struct pz13_capture *f) { (void)f;return fail_init; }
static int pm_runtime_force_suspend(struct device *d) { assert(!d->refs);return 0; }
static void schedule_delayed_work(struct delayed_work *w,unsigned int t) { assert(t>0);assert(!w->pending);w->pending=true; }
static void cancel_delayed_work_sync(struct delayed_work *w) {
 if(w->running) { assert(!pthread_join(w->worker,NULL));w->running=false; }
 w->pending=false;
}
#include "../camera/drivers/pz13-camera-lifecycle.h"

static void reset(struct pz13_capture *f) {
 assert(!f->client->dev.refs && !f->streaming && !f->deadline.running);
 faulted=attempted=false;stream_result=cleanup_error=0;
 fail_init=fail_write=fail_resume=fail_put=0;
 stream_starts=stream_stops=0;f->deadline.pending=false;
}
static void *worker(void *p) { deadline_work(p);return NULL; }
int main(void) {
 struct client client={0};
 struct pz13_capture f={.client=&client};
 current=&f;
 assert(!pthread_mutex_init(&f.lock.native,NULL));
 assert(!pthread_mutex_init(&f.stream_lock.native,NULL));
 for(int i=0;i<3;i++) {
  assert(!set_stream(&f.sd,1));assert(client.dev.refs==1);
  assert(!set_stream(&f.sd,1));assert(stream_starts==(unsigned)i+1);
  assert(system_suspend(&client.dev)==-EBUSY);
  assert(!set_stream(&f.sd,0));assert(!set_stream(&f.sd,0));
  assert(!client.dev.refs && stream_stops==(unsigned)i+1);
  assert(!system_suspend(&client.dev));
 }
 assert(set_stream(&f.sd,1)==-EOVERFLOW && !client.dev.refs);
 reset(&f);max_starts=0;stream_timeout_ms=0;
 for(int i=0;i<100;i++) {
  assert(!set_stream(&f.sd,1));assert(!f.deadline.pending);
  assert(!set_stream(&f.sd,0));assert(!client.dev.refs);
 }
 assert(stream_starts==100 && stream_stops==100);
 max_starts=3;stream_timeout_ms=15000;
 reset(&f);fail_resume=-ENODEV;
 assert(set_stream(&f.sd,1)==-ENODEV && faulted && !client.dev.refs);
 assert(set_stream(&f.sd,1)==-EIO);
 reset(&f);fail_init=-EIO;
 assert(set_stream(&f.sd,1)==-EIO && faulted && !client.dev.refs);
 reset(&f);assert(!set_stream(&f.sd,1));fail_write=-EREMOTEIO;
 assert(set_stream(&f.sd,0)==-EREMOTEIO && !client.dev.refs && faulted);
 reset(&f);assert(!set_stream(&f.sd,1));fail_put=-EIO;
 assert(set_stream(&f.sd,0)==-EIO && faulted && !client.dev.refs);
 reset(&f);assert(!set_stream(&f.sd,1));cleanup_error=-EIO;
 assert(set_stream(&f.sd,0)==-EIO && faulted && !client.dev.refs);
 reset(&f);assert(!set_stream(&f.sd,1));
 f.deadline.pending=false;deadline_work(&f.deadline.work);
 assert(faulted && stream_result==-ETIMEDOUT && !client.dev.refs);
 assert(set_stream(&f.sd,1)==-EIO && stream_starts==1);
 assert(set_stream(&f.sd,0)==-ETIMEDOUT);
 /* The worker is already dispatched and waiting for the control mutex.
  * stop must drain it without acquiring that mutex first (old deadlock).
  */
 for(int i=0;i<100;i++) {
  reset(&f);assert(!set_stream(&f.sd,1));
  mutex_lock(&f.lock);
  f.deadline.pending=false;f.deadline.running=true;
  assert(!pthread_create(&f.deadline.worker,NULL,worker,&f.deadline.work));
  mutex_unlock(&f.lock);
  assert(set_stream(&f.sd,0)==-ETIMEDOUT);
  assert(!client.dev.refs && stream_stops==1 && faulted);
 }
 reset(&f);f.removing=true;
 assert(set_stream(&f.sd,1)==-EIO && !client.dev.refs);
 assert(!pthread_mutex_destroy(&f.lock.native));
 assert(!pthread_mutex_destroy(&f.stream_lock.native));
 puts("PASS: repeat/duplicate starts, stop accounting, idle/active sleep, start/write/PM/cleanup failures, deadline latch, 100 concurrent worker drains, removal");
}
