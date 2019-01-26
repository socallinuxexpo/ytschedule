#!/usr/bin/python

from room.models import *
import time
import datetime
import pytz
import iso8601
from xml.etree.ElementTree import Element, SubElement, dump, parse, tostring, fromstring
import os
import sys
import django
#from daemon import Daemon

rundir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../run'))

path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(path)
os.environ["DJANGO_SETTINGS_MODULE"] = "ytschedule.settings.production"

TIME_ZONE = 'America/Los_Angeles'

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

    rooms = []
    if len(sys.argv) > 1:
        if sys.argv[1].lower() == "all":
            rooms = Room.objects.all()
        else:
            rooms.append(Room.objects.get(id=sys.argv[1]))
    else:
        rooms.append(Room.objects.first())

    for room in rooms:
        # print "[%i]%s -- %s" % (room.id, room.title, room.state)
        # room.update_description()
        # room.create_stream()
        room.republish()

#    talks = Talk.objects.filter(room=room)
#    for talk in talks:
#      talk.publish()
