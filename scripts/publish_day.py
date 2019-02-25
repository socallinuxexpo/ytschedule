#!/usr/bin/python

import time,datetime
import pytz
import iso8601
from xml.etree.ElementTree import Element, SubElement, dump, parse, tostring, fromstring
import os, sys
import django
from django.db.models import Q
#from daemon import Daemon

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
  logger.setLevel(logging.WARNING)

  ch = logging.StreamHandler(sys.stdout)
  ch.setLevel(logging.WARNING)
  logger.setLevel(logging.WARNING)
  logger.setLevel(logging.INFO)
  formatter = logging.Formatter('%(levelname)s - %(message)s')
  ch.setFormatter(formatter)
  logger.addHandler(ch)

  if len(sys.argv) > 1:
    days = int(sys.argv[1])
  else:
    days = 0

  now = datetime.datetime.now(tz)
  start = datetime.datetime(now.year,now.month,now.day+days)
  end = datetime.datetime(now.year,now.month,now.day+1+days)
  print "%s <==> %s" % (start, end)
  query = Room.objects.filter(Q(state="published") | Q(state="testing") | Q(state="live"))
  query = query.filter(start_time__lte=end)
  query = query.filter(end_time__gte=start)
  streams=0
  if len(query) > 0:
    for result in query:
      print result
      streams+=1
      talks = Talk.objects.filter(room=result).order_by('start_time')
      for talk in talks:
          print "--%s--%s" % (talk.start_time, talk)
          streams+=1
  print streams
  # rooms = []
  # if len(sys.argv) > 1:
  #   if sys.argv[1].lower() == "all":
  #     rooms = Room.objects.all()
  #   else:
  #     rooms.append( Room.objects.get(id=sys.argv[1]) )
  # else:
  #   rooms.append(Room.objects.first())
  #
  # for room in rooms:
    #print "[%i]%s -- %s" % (room.id, room.title, room.state)
    #room.update_description()
    #room.create_stream()
    # room.republish()

#    talks = Talk.objects.filter(room=room)
#    for talk in talks:
#      talk.publish()
