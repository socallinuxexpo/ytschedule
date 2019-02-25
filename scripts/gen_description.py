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
os.environ["DJANGO_SETTINGS_MODULE"] = "ytschedule.settings.production"


TIME_ZONE ='America/Los_Angeles'
from room.models import *

tz = pytz.timezone(TIME_ZONE)
time.tzset()
os.environ['TZ'] = 'America/Los_Angeles'
if __name__ == "__main__":
  django.setup()
  logger = logging.getLogger()
  logger.setLevel(logging.DEBUG)

  ch = logging.StreamHandler(sys.stdout)
  ch.setLevel(logging.DEBUG)
  formatter = logging.Formatter('%(levelname)s - %(message)s')
  ch.setFormatter(formatter)
  logger.addHandler(ch)

  for room in Room.objects.all():
    print room.title
    print YouTube.lt(room.start_time)
    talks = Talk.objects.filter(room=room).filter(start_time__gte=room.start_time).filter(end_time__lte=room.end_time)
    desc = "<p><a href=\"https://www.socallinuxexpo.org/scale/14x\">SCaLE 16x</a> - the 16th annual <a href=\"https://www.socallinuxexpo.org/\">Southern California Linux Expo</a> - the first-of-the-year Linux/Open Source software expo in North America, SCaLE 14X expects to host 150 exhibitors this year, along with nearly 130 sessions, tutorials and special events</p><p>SCaLE is the largest community-run open-source and free software conference in North America. It is held annually in Los Angeles.</p>\n"
    print len(talks)
    for talk in talks:
      diff=(talk.start_time-room.start_time).seconds
      diff += 300

      link="#t="
      hours = diff/3600
      if hours > 0:
        link+="%ih" % hours
      minutes=diff%3600/60
      if minutes > 0:
        link+="%im" % minutes
      seconds = (diff%3600)%60
      if seconds > 0:
        link += "%is" % seconds
      desc += "<a href=\"%s\">%s</a> to %s: <a href=\"%s\">%s</a><br/>\n" % (link, YouTube.lt(talk.start_time).strftime('%I:%M %p'),
                                                       YouTube.lt(talk.end_time).strftime('%I:%M %p %Z'),
                                                       talk.talk_url, talk.title)
    if room.title != "Ballroom A Saturday Jan. 23 - SCaLE 14x":
      print desc
    exit
  #print len(Talk.objects.all())
