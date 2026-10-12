#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""PZ13 camera application: full-field CPU preview, photos, video and rear focus.

The launcher supplies reviewed drivers and per-sensor IPA profiles. This app
does not load modules or change system permissions. --synthetic --exercise
tests the actual application actions without accessing any camera.
"""
import argparse
from datetime import datetime
import importlib.util
import json
import os
from pathlib import Path
import signal
import statistics
import subprocess
import threading
import time

CAMERAS={'front':'/base/soc@0/cci@ac16000/i2c-bus@1/camera@36',
         'rear':'/base/soc@0/cci@ac15000/i2c-bus@0/camera@36'}
GEOMETRY={'front':(2584,1944,1292,972),'rear':(4216,3136,2108,1568)}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profiles',type=Path)
    parser.add_argument('--output',type=Path,default=Path.home()/'Pictures/PZ13 Camera')
    parser.add_argument('--synthetic',action='store_true')
    parser.add_argument('--exercise',action='store_true')
    parser.add_argument('--exercise-sleep',action='store_true')
    parser.add_argument('--exercise-focus',action='store_true')
    parser.add_argument('--headless',action='store_true')
    parser.add_argument('--max-seconds',type=int,default=0)
    args=parser.parse_args()
    if args.max_seconds and not 10<=args.max_seconds<=1800:parser.error('Use zero or a 10..1800 second session limit')
    if not args.synthetic:
        if args.profiles is None:parser.error('Reviewed per-sensor profiles required')
        for model in ('ov5675','ov13858'):
            if not (args.profiles/'simple'/(model+'.yaml')).is_file():parser.error('Missing '+model+' profile')
        os.environ['LIBCAMERA_IPA_CONFIG_PATH']=str(args.profiles.resolve())
    os.environ.pop('LIBCAMERA_SIMPLE_TUNING_FILE',None)
    os.environ['LIBCAMERA_PIPELINES_MATCH_LIST']='simple'
    os.environ['LIBCAMERA_SOFTISP_MODE']='cpu'
    os.umask(0o077)
    args.output.mkdir(parents=True,exist_ok=True,mode=0o700)
    import gi
    gi.require_version('Gst','1.0')
    from gi.repository import Gst,GLib,Gio
    Gst.init(None)
    Gtk=None
    if not args.headless:
        gi.require_version('Gtk','3.0')
        from gi.repository import Gtk
        if not Gtk.init_check()[0]:raise RuntimeError('An unlocked graphical session is required')

    class Camera:
        def __init__(self):
            self.side='front';self.pipeline=None;self.bus=None;self.widget=None
            self.recording=None;self.last=None;self.frame_count=0
            self.synthetic_focus=265
            self.video_pipeline=None;self.video_bus=None;self.video_source=None
            self.video_pts=None;self.video_frames=0
            self.lock=threading.Lock();self.focus_cancel=threading.Event();self.focus_thread=None
            self.failed=False;self.closed=False;self.events=[];self.session=time.monotonic()
            self.loop=GLib.MainLoop();self.window=None
            self.preview_box=None;self.status=None;self.focus_slider=None
            self.record_button=None;self.switch_button=None;self.focus_button=None
            self.sleep_fd=None;self.sleep_proxy=None;self.resume_needed=False
            if Gtk:self.ui()
            if not args.synthetic:
                self.sleep_proxy=Gio.DBusProxy.new_for_bus_sync(Gio.BusType.SYSTEM,
                    Gio.DBusProxyFlags.DO_NOT_LOAD_PROPERTIES,None,'org.freedesktop.login1',
                    '/org/freedesktop/login1','org.freedesktop.login1.Manager',None)
                self.sleep_proxy.connect('g-signal',self.sleep_signal)
                self.inhibit_sleep()

        def inhibit_sleep(self):
            if self.sleep_proxy is None or self.sleep_fd is not None:return
            result,fds=self.sleep_proxy.call_with_unix_fd_list_sync('Inhibit',
                GLib.Variant('(ssss)',('sleep','PZ13 Camera','Finish camera capture before sleep','delay')),
                Gio.DBusCallFlags.NONE,2000,None,None)
            self.sleep_fd=fds.get(result.unpack()[0])

        def release_inhibitor(self):
            if self.sleep_fd is not None:os.close(self.sleep_fd);self.sleep_fd=None

        def sleep_signal(self,_proxy,_sender,name,parameters):
            if name=='PrepareForSleep':
                self.action(self.pause_for_sleep if parameters.unpack()[0] else self.resume_after_sleep)

        def pause_for_sleep(self):
            self.resume_needed=self.pipeline is not None
            try:self.stop();self.note('Camera paused for sleep')
            finally:self.release_inhibitor()

        def resume_after_sleep(self):
            self.inhibit_sleep()
            if self.resume_needed and not self.closed and not self.failed:self.start()
            self.resume_needed=False

        def note(self,message,**details):
            event={'at_s':round(time.monotonic()-self.session,3),'event':message,**details}
            self.events.append(event);print(json.dumps(event),flush=True)
            if self.status:self.status.set_text(message)
            return False

        def ui(self):
            self.window=Gtk.Window(title='PZ13 Camera');self.window.set_default_size(1000,780)
            self.window.connect('delete-event',lambda *_:self.close())
            box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=8)
            box.set_border_width(12);self.window.add(box)
            self.preview_box=Gtk.Box();box.pack_start(self.preview_box,True,True,0)
            row=Gtk.Box(spacing=8);box.pack_start(row,False,False,0)
            for label,callback in [('Switch camera',self.switch),('Take photo',self.photo),
                                   ('Record silent video',self.toggle_record),('Focus',self.autofocus)]:
                button=Gtk.Button(label=label);button.connect('clicked',lambda _,f=callback:self.action(f))
                row.pack_start(button,True,True,0)
                if label=='Record silent video':self.record_button=button
                elif label=='Switch camera':self.switch_button=button
                elif label=='Focus':self.focus_button=button
            focus=Gtk.Box(spacing=8);box.pack_start(focus,False,False,0)
            focus.pack_start(Gtk.Label(label='Rear focus · far → near'),False,False,0)
            self.focus_slider=Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL,265,508,1)
            self.focus_slider.set_value(265);self.focus_slider.set_draw_value(False)
            self.focus_slider.connect('button-release-event',lambda *_:self.action(self.manual_focus))
            self.focus_slider.connect('key-release-event',lambda *_:self.action(self.manual_focus))
            focus.pack_start(self.focus_slider,True,True,0)
            self.status=Gtk.Label(label='Starting camera…');self.status.set_line_wrap(True)
            box.pack_start(self.status,False,False,0)
            self.window.show_all()

        def action(self,callback):
            try:callback()
            except Exception as error:self.error(error)
            return False

        def error(self,error):
            self.failed=True;self.note('Camera stopped: '+str(error))
            try:self.stop()
            except Exception as cleanup:self.note('Cleanup error: '+str(cleanup))
            if args.exercise:self.close()

        def start(self):
            if self.failed or self.closed:raise RuntimeError('Reopen the app after reviewing the camera error')
            self.last=None;self.frame_count=0
            w,h,sw,sh=GEOMETRY[self.side]
            source=('videotestsrc is-live=true pattern='+('smpte' if self.side=='front' else 'ball') if args.synthetic else
                    'libcamerasrc camera-name='+CAMERAS[self.side]+' gamma=3.2')
            q='queue max-size-buffers=2 max-size-bytes=0 max-size-time=0'
            pipeline=(f'{source} ! video/x-raw,format=BGR,width={w},height={h} ! tee name=original '
                      f'original. ! {q} leaky=downstream ! appsink name=fullphoto max-buffers=1 drop=true sync=false '
                      f'original. ! {q} ! '
                      f'videoscale method=1 ! video/x-raw,width={sw},height={sh} ! videoconvert ! '
                      'video/x-raw,format=I420 ! videomedian filtersize=5 lum-only=false ! tee name=frames '
                      f'frames. ! {q} leaky=downstream ! videoconvert ! '
                      +('video/x-raw,format=BGRx ! gtksink name=preview sync=false ' if Gtk else 'fakesink name=preview sync=false ')
                      +f'frames. ! {q} ! jpegenc quality=90 ! tee name=jpeg '
                      +f'jpeg. ! {q} leaky=downstream ! appsink name=photo emit-signals=true max-buffers=1 drop=true sync=false ')
            self.pipeline=Gst.parse_launch(pipeline)
            self.pipeline.get_by_name('photo').connect('new-sample',self.sample)
            self.bus=self.pipeline.get_bus();self.bus.add_signal_watch()
            self.bus.connect('message',self.message)
            if Gtk:
                self.widget=self.pipeline.get_by_name('preview').get_property('widget')
                self.preview_box.pack_start(self.widget,True,True,0);self.widget.show()
                self.focus_slider.set_sensitive(self.side=='rear')
                if self.side=='rear':self.focus_slider.set_value(self.current_focus())
                self.focus_button.set_sensitive(self.side=='rear')
                self.switch_button.set_label('Use rear camera' if self.side=='front' else 'Use front camera')
                self.record_button.set_label('Record silent video')
            if self.pipeline.set_state(Gst.State.PLAYING)==Gst.StateChangeReturn.FAILURE:
                raise RuntimeError('Camera could not start')
            self.note('Preview · '+self.side,camera=self.side)

        def sample(self,sink):
            sample=sink.emit('pull-sample')
            if sample is None:return Gst.FlowReturn.EOS
            buffer=sample.get_buffer()
            data=buffer.extract_dup(0,buffer.get_size())
            with self.lock:
                self.frame_count+=1;self.last=(time.monotonic(),self.frame_count,data)
                if self.video_source is not None:
                    if buffer.pts==Gst.CLOCK_TIME_NONE:
                        GLib.idle_add(self.error,RuntimeError('Camera frame has no timestamp'))
                    else:
                        if self.video_pts is None:
                            self.video_pts=buffer.pts
                            self.video_source.set_property('caps',sample.get_caps())
                        recorded=buffer.copy()
                        recorded.pts=buffer.pts-self.video_pts
                        recorded.dts=Gst.CLOCK_TIME_NONE
                        result=self.video_source.emit('push-buffer',recorded)
                        if result!=Gst.FlowReturn.OK:
                            GLib.idle_add(self.error,RuntimeError('Video writer stopped accepting frames'))
                        else:self.video_frames+=1
            return Gst.FlowReturn.OK

        def message(self,bus,message):
            if bus not in (self.bus,self.video_bus):return
            if message.type==Gst.MessageType.ERROR:
                error,debug=message.parse_error();self.error(str(error)+' '+str(debug))

        def cancel_focus(self):
            self.focus_cancel.set()
            if self.focus_thread:
                self.focus_thread.join(timeout=4)
                if self.focus_thread.is_alive():raise RuntimeError('Focus operation did not stop')
                self.focus_thread=None

        def stop(self):
            self.cancel_focus()
            video_error=None
            try:self.stop_video()
            except Exception as error:video_error=error
            if not self.pipeline:return
            pipeline=self.pipeline;self.pipeline=None
            bus=self.bus;self.bus=None;bus.remove_signal_watch()
            try:
                result=pipeline.set_state(Gst.State.NULL)
                state=pipeline.get_state(5*Gst.SECOND)
                if result==Gst.StateChangeReturn.FAILURE or state.state!=Gst.State.NULL:
                    raise RuntimeError('Camera did not release')
            finally:
                if self.widget:
                    self.preview_box.remove(self.widget);self.widget=None
                self.last=None
            if video_error:raise video_error

        def stop_video(self):
            with self.lock:
                source=self.video_source;self.video_source=None
            pipeline=self.video_pipeline
            if pipeline is None:return
            self.video_pipeline=None
            bus=self.video_bus;self.video_bus=None;bus.remove_signal_watch()
            saved=self.recording;self.recording=None
            try:
                source.emit('end-of-stream')
                msg=bus.timed_pop_filtered(2*Gst.SECOND,Gst.MessageType.EOS|Gst.MessageType.ERROR)
                if msg is None or msg.type!=Gst.MessageType.EOS:
                    raise RuntimeError('Video could not finish; partial file retained')
            finally:
                pipeline.set_state(Gst.State.NULL)
                pipeline.get_state(3*Gst.SECOND)
                if self.record_button:self.record_button.set_label('Record silent video')
            self.note('Video saved',path=str(saved),frames=self.video_frames)

        def path(self,suffix):
            return args.output/(datetime.now().strftime('%Y%m%d-%H%M%S-%f')+'-'+self.side+suffix)

        def photo(self):
            with self.lock:sample=self.last
            if sample is None or time.monotonic()-sample[0]>2:
                self.note('Wait for a live image before taking a photo');return
            original=self.pipeline.get_by_name('fullphoto').emit('try-pull-sample',0)
            if original is None:
                self.note('Wait for a full-resolution photo frame');return
            # Encode only the requested frame. Preview/video keep their bounded
            # queues and the sensor keeps streaming with unchanged exposure.
            encoder=Gst.parse_launch('appsrc name=input format=time ! videoconvert '
                '! video/x-raw,format=I420 ! videomedian filtersize=5 lum-only=false '
                '! jpegenc quality=95 ! appsink name=output max-buffers=1 sync=false')
            try:
                source=encoder.get_by_name('input');source.set_property('caps',original.get_caps())
                if encoder.set_state(Gst.State.PLAYING)==Gst.StateChangeReturn.FAILURE:
                    raise RuntimeError('Photo encoder could not start')
                frame=original.get_buffer().copy();frame.pts=0;frame.dts=Gst.CLOCK_TIME_NONE
                if source.emit('push-buffer',frame)!=Gst.FlowReturn.OK:
                    raise RuntimeError('Photo encoder rejected frame')
                source.emit('end-of-stream')
                encoded=encoder.get_by_name('output').emit('try-pull-sample',5*Gst.SECOND)
                if encoded is None:raise RuntimeError('Full-resolution photo did not finish')
                buffer=encoded.get_buffer();data=buffer.extract_dup(0,buffer.get_size())
            finally:
                encoder.set_state(Gst.State.NULL);encoder.get_state(3*Gst.SECOND)
            path=self.path('.jpg')
            with path.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
            self.note('Photo saved',path=str(path),frame=sample[1],resolution=GEOMETRY[self.side][:2])

        def switch(self):
            self.stop();self.side='rear' if self.side=='front' else 'front';self.start()

        def toggle_record(self):
            if self.video_pipeline is not None:self.stop_video();return
            with self.lock:ready=self.last is not None
            if not self.pipeline or not ready:
                self.note('Wait for a live image before recording');return
            pipeline=Gst.parse_launch('appsrc name=source is-live=true format=time block=false '
                'max-buffers=8 max-bytes=16777216 leaky-type=downstream '
                '! queue max-size-buffers=8 max-size-bytes=16777216 max-size-time=0 '
                '! matroskamux ! filesink name=record')
            path=self.path('.mkv');pipeline.get_by_name('record').set_property('location',str(path))
            self.video_pipeline=pipeline;self.video_bus=pipeline.get_bus()
            self.video_bus.add_signal_watch();self.video_bus.connect('message',self.message)
            if pipeline.set_state(Gst.State.PLAYING)==Gst.StateChangeReturn.FAILURE:
                raise RuntimeError('Video writer could not start')
            self.recording=path
            with self.lock:
                self.video_pts=None;self.video_frames=0
                self.video_source=pipeline.get_by_name('source')
            if self.record_button:self.record_button.set_label('Stop video')
            self.note('Recording silent video · '+self.side,path=str(path))

        def rear_device(self):
            candidates=[Path('/dev')/p.name for p in Path('/sys/class/video4linux').glob('v4l-subdev*')
                        if (p/'name').read_text().strip().startswith('ov13858 ')]
            if len(candidates)!=1:raise RuntimeError('Rear focus control unavailable')
            return str(candidates[0])

        def move_focus(self,code):
            if self.side!='rear' or not self.pipeline:raise RuntimeError('Select the rear camera first')
            if not 265<=code<=508:raise ValueError('Focus outside calibrated range')
            if args.synthetic:self.synthetic_focus=code;return
            subprocess.run(['v4l2-ctl','-d',self.rear_device(),'--set-ctrl=focus_absolute='+str(code)],
                           check=True,timeout=2,capture_output=True)

        def current_focus(self):
            if args.synthetic:return self.synthetic_focus
            text=subprocess.check_output(['v4l2-ctl','-d',self.rear_device(),
                '--get-ctrl=focus_absolute'],text=True,timeout=2)
            code=int(text.rsplit(':',1)[1].strip())
            if not 265<=code<=508:raise RuntimeError('Rear focus readback outside calibrated range')
            return code

        def exposure_state(self):
            if args.synthetic:return 'synthetic'
            return subprocess.check_output(['v4l2-ctl','-d',self.rear_device(),
                '--get-ctrl=exposure,analogue_gain'],text=True,timeout=2).strip()

        def manual_focus(self):
            if self.side!='rear':return
            self.cancel_focus();code=round(self.focus_slider.get_value());self.move_focus(code)
            self.note('Rear focus set',code=code)

        def autofocus(self):
            if self.side!='rear':self.note('The front camera has fixed focus');return
            if self.focus_thread and self.focus_thread.is_alive():return
            self.focus_cancel.clear();self.note('Focusing on the center — keep the subject still')
            original=self.current_focus()
            def search():
                try:
                    spec=importlib.util.spec_from_file_location('metric',Path(__file__).with_name('score-pz13-camera-focus.py'))
                    metric=importlib.util.module_from_spec(spec);spec.loader.exec_module(metric)
                    gi.require_version('GdkPixbuf','2.0')
                    from gi.repository import GdkPixbuf
                    scores=[]
                    def measure(code,stage):
                        if self.focus_cancel.is_set():return None
                        controls_before=self.exposure_state()
                        self.move_focus(code)
                        moved=time.monotonic()
                        if self.focus_cancel.wait(.65):return None
                        measured=[];last_frame=-1
                        for _ in range(3):
                            if self.focus_cancel.wait(.15):return None
                            with self.lock:sample=self.last
                            if sample is None or sample[1]==last_frame or sample[0]<moved:
                                raise RuntimeError('No fresh focus frame')
                            last_frame=sample[1]
                            loader=GdkPixbuf.PixbufLoader.new_with_type('jpeg')
                            loader.write(sample[2]);loader.close();p=loader.get_pixbuf()
                            measured.append(metric.score_focus_pixbuf(p))
                        value={'code':code,'stage':stage,'score':statistics.median(v['score'] for v in measured),
                               'luma':statistics.median(v['mean_luma'] for v in measured),
                               'scene_luma':statistics.median(v['scene_luma'] for v in measured),
                               'controls_before':controls_before,'controls_after':self.exposure_state()}
                        scores.append(value);return value
                    coarse=[]
                    for code in (265,296,326,357,387,418,448,478,508):
                        value=measure(code,'coarse')
                        if value is None:return
                        coarse.append(value)
                    best=max(coarse,key=lambda v:v['score'])
                    enough=metric.stable_measurements(coarse) and best['score']>statistics.median(v['score'] for v in coarse)*1.08
                    if enough:
                        coarse_score=best['score']
                        fine=[]
                        for code in sorted({max(265,min(508,best['code']+offset)) for offset in (-10,-5,0,5,10)}):
                            value=measure(code,'fine')
                            if value is None:return
                            fine.append(value)
                        best=max(fine,key=lambda v:v['score'])
                        verified=measure(best['code'],'verify')
                        if verified is None:return
                        enough=metric.verified_focus(scores,coarse_score,best['score'],verified['score'])
                    if self.focus_cancel.is_set():return
                    chosen=best['code'] if enough else original
                    self.move_focus(chosen)
                    def finish():
                        if self.closed or self.side!='rear' or self.focus_cancel.is_set():return False
                        if self.focus_slider:self.focus_slider.set_value(chosen)
                        self.note('Focus set' if enough else 'Focus uncertain — use a brighter detailed subject or the slider',
                                  code=chosen,measurements=scores)
                        return False
                    GLib.idle_add(finish)
                except Exception as error:GLib.idle_add(self.error,error)
            self.focus_thread=threading.Thread(target=search,daemon=True);self.focus_thread.start()

        def close(self):
            if self.closed:return True
            self.closed=True
            try:self.stop()
            except Exception as error:self.failed=True;self.note('Cleanup error: '+str(error))
            self.release_inhibitor()
            self.note('Camera closed',result='FAILED' if self.failed else 'PASSED')
            report=args.output/('session-'+datetime.now().strftime('%Y%m%d-%H%M%S-%f')+'.json')
            report.write_text(json.dumps({'result':'FAILED' if self.failed else 'PASSED',
                                         'synthetic':args.synthetic,'events':self.events},indent=2)+'\n')
            if self.window:self.window.destroy()
            self.loop.quit();return True

        def exercise(self):
            # Same callbacks as the visible buttons, including video EOS and switching.
            def focus_reopen():
                self.move_focus(387)
                self.stop();self.start()
                if self.current_focus()!=387:raise RuntimeError('Rear focus setting changed across reopening')
                if self.focus_slider and round(self.focus_slider.get_value())!=387:
                    raise RuntimeError('Rear focus slider differs from the driver')
                self.note('Rear focus preserved across reopening',code=387)
            steps=[self.photo,self.toggle_record,self.photo,self.toggle_record,self.switch,
                   self.photo,self.toggle_record,self.photo,self.toggle_record,self.switch,self.photo,self.close]
            if args.exercise_focus:steps[5:5]=[focus_reopen,self.autofocus]
            if args.exercise_sleep:steps[-1:-1]=[self.pause_for_sleep,self.resume_after_sleep,self.photo]
            def next_step():
                if self.closed:return False
                if self.focus_thread and self.focus_thread.is_alive():
                    GLib.timeout_add_seconds(1,next_step);return False
                callback=steps.pop(0);self.action(callback)
                if steps and not self.closed:
                    delay=8 if callback in (self.switch,self.resume_after_sleep,focus_reopen) else 3
                    GLib.timeout_add_seconds(delay,next_step)
                return False
            GLib.timeout_add_seconds(8,next_step)

    camera=Camera()
    GLib.unix_signal_add(GLib.PRIORITY_DEFAULT,signal.SIGTERM,camera.close)
    GLib.unix_signal_add(GLib.PRIORITY_DEFAULT,signal.SIGINT,camera.close)
    if args.max_seconds:GLib.timeout_add_seconds(args.max_seconds,lambda:camera.close() and False)
    camera.action(camera.start)
    if args.exercise:camera.exercise()
    if not camera.closed:camera.loop.run()
    raise SystemExit(1 if camera.failed else 0)


if __name__=='__main__':main()
