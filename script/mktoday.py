#!/usr/bin/env python
from room.models import *
"""
Create a Room with talks for testing Daemon
"""
import sys
import os
import time
import pytz
import logging
import datetime
import django
from daemon import Daemon

rundir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../run'))

path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(path)


TIME_ZONE = 'America/Los_Angeles'

tz = pytz.timezone(TIME_ZONE)
utc = pytz.timezone("UTC")
if __name__ == "__main__":
    django.setup()

    DAY_LENGTH = 1  # hours
    NUM_TALKS = 4
    START_IN = 20  # minutes
    PUBLISH = True
    room_name = "Room 107"

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    now = datetime.datetime.now(tz)
    start_time = datetime.datetime(now.year, now.month, now.day, now.hour,
                                   now.minute, 0, 0, tzinfo=tz)+datetime.timedelta(minutes=START_IN)
    #start_time = now + datetime.timedelta(0,60*START_IN)
    end_time = start_time + datetime.timedelta(0, 60*60*DAY_LENGTH)

    print "Room Start=%s" % start_time
    print "Room End=  %s" % end_time
    room = Room(title="Room_%s" % now.strftime("%m%d"),
                name=room_name, start_time=start_time, end_time=end_time)
    room.save()

    talk_length = 60*60*DAY_LENGTH/8

    for index in range(0, NUM_TALKS):
        title = "%s: Talk #%i" % (room.title, index+1)
        print title
        talk_start = start_time + datetime.timedelta(0, talk_length*index)
        talk_end = start_time + \
            datetime.timedelta(0, talk_length*index+talk_length)
        print "Talk Start=%s" % talk_start
        print "Talk End=  %s" % talk_end
        talk = Talk(room_id=room.id, title=title,
                    start_time=talk_start, end_time=talk_end,
                    description="Description for: %s" % title)
        talk.save()
