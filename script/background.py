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

from room.models import Room, Talk

TIME_ZONE ='America/Chicago'

tz = pytz.timezone(TIME_ZONE)

class YtSchedule(Daemon):
  def __init__(self, *args, **kwargs):
    Daemon.__init__(self, *args, **kwargs)
    django.setup()

  def run(self): #Define what tasks/processes to daemonize
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', 
                        filename=os.path.join(rundir, "testdaemon.log"), 
                        level=logging.DEBUG)
    while True:
      logging.debug("Debug message")
      logging.info("Info message")
      logging.warn("Warning message")
      logging.error("Error message (%s)" % datetime.datetime.now())
      
      now = datetime.datetime.now(tz)
      query = Room.objects.filter(start_time__lte=now)
      query = query.filter(end_time__gte=now+datetime.timedelta(seconds=10*60))
      if len(query) > 0:
        for result in query:
          print "[%s]: %s -- %s"%(result.title, result.start_time, result.end_time)
          if result.state == 'planned':
            result.publish_stream()
          if result.state == 'created':
            result.is_ready()
          if result.state == 'ready':
            result.stream()
          if result.state == 'inactive':
            result.assess()
          if result.state == 'error':
            result.assess()

      q = Talk.objects.filter(start_time__lte=now)
      q = q.filter(end_time__gte=now+datetime.timedelta(seconds=10*60))
      if len(q) > 0:
        for result in q:
          print "[%s]: %s -- %s"%(result.title, result.start_time, result.end_time)
      
      now = datetime.datetime.now(tz)
      nexttime = now.replace(second=0,microsecond=0)+datetime.timedelta(seconds=60)
      diff = (nexttime - now).total_seconds()
      logging.debug("Now: %s, Target: %s, Diff: %s" % (now, nexttime, diff))
      time.sleep( diff )

if __name__ == "__main__":
    daemon = YtSchedule( os.path.join(rundir, 'daemon-py-test.pid') ) #Define a pidfile location (typically located in /tmp or /var/run)
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        elif 'status' == sys.argv[1]:
            daemon.status()
        elif 'run' == sys.argv[1]:
            daemon.run()
        else:
            sys.stdout.write("Unknown command\n")
            sys.exit(2)
        sys.exit(0)
    else:
        sys.stdout.write("Usage: %s start|stop|restart|status\n" % sys.argv[0])
        sys.exit(2)
