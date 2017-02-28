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
#!/bin/bash
#first pass a a pipeline to push from SNP-6200 rtsp to gst-switch.

#this test pipe line should provide data from snp-6200 to gst-switch
ipaddress=$1

gst-launch-1.0 -v -m rtspsrc location=rtsp://${ipaddress}/1 latency=0 ntp-sync=true is-live=true do-timestamp=true name=camera \
  camera. ! "application/x-rtp,media=video,payload=96" ! rtph264depay ! queue ! \
  vaapiparse_h264 ! decodebin ! typefind name=finder ! \
   video/x-raw, format=I420, pixel-aspect-ratio=1/1, interlace-mode=progressive ! \
  queue ! fpsdisplaysink sync=false \
  camera. ! rtpmp4gdepay ! queue ! audio/mpeg, mpegversion=4, stream-format=raw ! aacparse ! typefind ! faad ! queue ! autoaudiosink silent=0 
exit
