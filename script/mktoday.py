#!/usr/bin/env python
"""
Unit test/basic Daemon-Python implementation
"""
import sys, os
import time, pytz
import logging
import datetime
import django
from daemon import Daemon

rundir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../run'))

path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(path)
os.environ["DJANGO_SETTINGS_MODULE"] = "ytschedule.settings"

from room.models import *

TIME_ZONE ='America/Chicago'

tz = pytz.timezone(TIME_ZONE)

if __name__ == "__main__":
  django.setup()
  now = datetime.datetime.now(tz)
  morning = now.replace(hour=9,minute=0,second=0,microsecond=0)
  q = Room.objects.filter(start_time__gte=morning)
  if len(q) == 0:
    print "not found"
    endtime = morning+datetime.timedelta(seconds=24*3600)
    room = Room(name="Room_%s"%now.strftime("%m%d"), title="Title of Room %s"%now.strftime("%m%d%Y"), start_time=morning,
                 end_time=endtime)
    room.save()
  else:
    print "found"
    room = q[0]

  print room.start_time.astimezone(tz)
  print room.end_time.astimezone(tz)

  hours = (room.end_time - room.start_time).seconds/3600
  
  for index in range(0, hours):
    start = morning.replace(hour=morning.hour+index,minute=0,second=0)
    end = morning.replace(hour=morning.hour+(index+1),minute=0,second=0)
    print "%s -- %s" %(start, end)
    q = Talk.objects.filter(start_time__gte=start)
    if len(q) == 0:
      tmp = Talk(room_id=room.id, name="Talk at %s"%start.strftime("%H:%M"), title="Title of talk at %s"%start, start_time=start, end_time=end)
      tmp.save()
    else:
      tmp = q[0]
    print tmp.title

  nexttime = now.replace(minute=now.minute+1,second=0)
  q = Room.objects.filter(start_time__gte=now)
  q = q.filter(start_time__lt=now.replace(minute=now.minute+5))
  print q

  
