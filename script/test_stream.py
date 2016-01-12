#!/usr/bin/python3

import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst, GstVideo, Gtk
from pprint import pprint

GObject.threads_init()
Gst.init(None)
loop=0

class Webcam():
  playing=True
  def __init__(self):
    # Create GStreamer pipeline
    stream_id = "mproctor13.w1x1-5akr-ghfm-2kcp"
    launch ="flvmux streamable=true name=mux ! queue ! "
    launch +="rtmpsink location=\"rtmp://a.rtmp.youtube.com/live2/x/%s?videoKeyframeFrequency=1&totalDatarate=5128 "  % stream_id
    launch +="flashVer=\\\"FME/3.0%%20(compatible;%%20FMSc%201.0)\\\" swfUrl=rtmp://a.rtmp.youtube.com/live2\" "
    launch +="audiotestsrc is-live=true ! capsfilter caps=\"audio/x-raw,format=S16LE,endianness=1234,signed=true,width=16,depth=16,rate=44100,channels=2\" ! "
    #launch +="audiotestsrc is-live=true ! \"format=S16LE,endianness=1234,signed=true,width=16,depth=16,rate=44100,channels=2\" ! "
    launch +="queue ! voaacenc bitrate=128000 ! aacparse ! queue ! mux. "
    launch +="videotestsrc pattern=smpte is-live=true ! capsfilter caps=\"video/x-raw,width=1920,height=1080\" ! "
    #launch = "videotestsrc pattern=smpte is-live=true ! "
    #launch +="queue ! "
    launch +="queue ! clockoverlay text=\"Generated at: \" auto-resize=true font-desc=\"Sans, 42\" "
    launch +="time-format=\"%m/%d/%Y %H:%M:%S\" halignment=center valignment=center ! "
    #launch +="time-format=\"%%m/%%d/%%Y %%H:%%M:%%S\" halignment=center valignment=center ! "
    launch +="vaapiencode_h264 bitrate=3000 keyframe-period=60 max-bframes=0 cabac=true rate-control=2 ! "
    launch +="capsfilter caps=\"video/x-h264,stream-format=avc,profile=main\" ! h264parse ! "
    #launch +="queue name=encodeded ! mux. "
    launch +="queue ! mux. "
    #launch +="flashVer=\"FME/3.0%20(compatible;%20FMSc%201.0)\" swfUrl=rtmp://a.rtmp.youtube.com/live2\""  % stream_id
    print(launch) 
    #exit(1)
    self.pipeline = Gst.parse_launch( launch )

    # Create bus to get events from GStreamer pipeline
    self.bus = self.pipeline.get_bus()
    self.bus.add_signal_watch()
    self.bus.connect('message::error', self.on_error)
    
    self.bus.enable_sync_message_emission()
    self.bus.connect('message', self.on_sync_message)
           
    #self.pipeline.set_state(Gst.STATE_PLAYING)
    #self.start()
    
  def run(self):
    print("running")
    self.pipeline.set_state(Gst.State.PLAYING)
    try:
      while (self.playing == True):
        pass
    except KeyboardInterrupt:
      print("Shutdown facedetect server ...")

  def on_sync_message(self, bus, msg):
    print("Got message from: ", msg.src.name)
    t = msg.type
    if t == Gst.MessageType.EOS:
      self.player.set_state(Gst.State.NULL)
      self.playing = False
    elif t == Gst.MessageType.INFO:
      print("Got info message.")
    else:
      print("Other")


  def on_error(self, bus, msg):
    print('on_error():', msg.parse_error())

if __name__ == '__main__':
  webcam = Webcam()
  webcam.run()

'''
#!/bin/bash
videobr=3072
overlay="queue ! clockoverlay text=\"Generated at: \" auto-resize=true font-desc=\"Sans, 42\" time-format=\"%m/%d/%Y %H:%M:%S\" halignment=center valignment=center !"

#  audio. ! mux. \
gst-launch-1.0 -v \
  videotestsrc pattern=smpte is-live=true ! video/x-raw,width=1920,height=1080 ! \
  queue ! $overlay \
  vaapiencode_h264 bitrate=5000 keyframe-period=60 max-bframes=0 cabac=true rate-control=2 ! \
  "video/x-h264,stream-format=avc,profile=main" ! \
  queue ! mux. \
  audiotestsrc is-live=true ! "audio/x-raw,format=S16LE,endianness=1234,signed=true,width=16,depth=16,rate=44100,channels=2" ! \
  queue ! voaacenc bitrate=128000 ! aacparse ! queue ! mux. \
  flvmux streamable=true name=mux ! queue ! \
  rtmpsink location="rtmp://a.rtmp.youtube.com/live2/x/$1?videoKeyframeFrequency=1&totalDatarate=5128 app=live2 flashVer=\"FME/3.0%20(compatible;%20FMSc%201.0)\" swfUrl=rtmp://a.rtmp.youtube.com/live2"


'''
