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
