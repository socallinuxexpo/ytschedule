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
from daemon import Daemon

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
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    if len(sys.argv) > 1:
        room = Room.objects.get(id=sys.argv[1])
    else:
        room = Room.objects.first()

    logger.info(room.title)
    logger.info(room.state)

    print "Stream State=[%s]" % room.check_state()

    print YouTube.broadcast_status(room.broadcast_id)

    # print YouTube.set_broadcast_status(room.broadcast_id, 'testing')
    print "\n\n"
    print YouTube.broadcast_status('4S5xZmKA328')
    # print YouTube.set_broadcast_status(room.broadcast_id, 'live')
