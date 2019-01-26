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
import pprint
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
        valid_status = ['active', 'all', 'completed', 'upcoming']
        if sys.argv[1] in valid_status:
            status = sys.argv[1]
        else:
            print "Status must be 'active', 'all', 'completed', 'upcoming'"
            exit(1)
    else:
        status = 'all'

    print YouTube.list_stream_health()

    #results = YouTube.list_broadcast(status)
    # print "Showing %s of %s results." % (len(results['items']), results['pageInfo']['totalResults'])

    # print results['pageInfo']['totalResults']
    # print len(results['items'])
    # for broadcast in results['items']:
    #  print "[%s] video_id=%s" % (broadcast['status']['lifeCycleStatus'], broadcast['id'])
    # pprint.pprint(results)
