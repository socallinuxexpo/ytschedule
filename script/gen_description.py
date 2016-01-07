#!/usr/bin/python

import time,datetime
import pytz
import iso8601
from xml.etree.ElementTree import Element, SubElement, dump, parse, tostring, fromstring
import os, sys
import django
from daemon import Daemon

rundir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../run'))

path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(path)
os.environ["DJANGO_SETTINGS_MODULE"] = "ytschedule.settings"

from room.models import *

TIME_ZONE ='America/Los_Angeles'

tz = pytz.timezone(TIME_ZONE)
time.tzset()
os.environ['TZ'] = 'America/Los_Angeles'
if __name__ == "__main__":
  django.setup()
  for room in Room.objects.all():
    #print room.name
    print room.start_time
    talks = Talk.objects.filter(room=room).filter(start_time__gte=room.start_time).filter(end_time__lte=room.end_time)
    desc = ""
    for talk in talks:
      desc += "%s to %s: <a href=\"%s\">%s</a><br/>" % (talk.start_time.strftime('%I:%M %p'), 
                                                       talk.end_time.strftime('%I:%M %p'), 
                                                       talk.talk_url, talk.title)
      print desc
  #print len(Talk.objects.all())


