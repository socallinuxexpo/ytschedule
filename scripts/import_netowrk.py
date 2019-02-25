#!/usr/bin/python

import time,datetime
import pytz
import iso8601
from xml.etree.ElementTree import Element, SubElement, dump, parse, tostring, fromstring
import os, sys
import django
import json
from pprint import pprint

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

  if len(sys.argv) > 1:
    filename = sys.argv[1]
  else:
    filename = 'managed_hosts.json'
  
  with open(filename) as data_file:    
    hosts = json.load(data_file)
  pprint.pprint(hosts)
  
  for room in Room.objects.all():
    logger.debug("Configuring %s" % room.podium_name())
    ipaddress = ""
    for key, value in hosts['maps'].iteritems():
      if room.podium_name() in value:
        ipaddress = key
        logger.info("Found %s's ipaddress is %s" % (room.podium_name(), ipaddress))
        break
    if ipaddress != "":
      for key, value in hosts['dhcp-host'].iteritems():
        if key == ipaddress:
          logger.info("Found %s's MAC Address is %s" % (ipaddress, key))
          room.mac_address = value
          room.save()


  #logger.info(room.title)
  #logger.info(room.state)

  #print "Stream State=[%s]" % room.check_state()
 
  #print YouTube.broadcast_status(room.broadcast_id)
  
  #print room.set_complete()

