#!/usr/bin/env python
"""
Unit test/basic Daemon-Python implementation
"""
import sys, os
import time, pytz
import logging
from logstash_formatter import LogstashFormatterV1
import datetime
import django
from daemon import Daemon


path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
rundir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../run'))
sys.path.append(path)
os.environ["DJANGO_SETTINGS_MODULE"] = "ytschedule.settings"

from room.models import Room, Talk

TIME_ZONE ='America/Los_Angeles'
SLEEP_TIME=30
tz = pytz.timezone(TIME_ZONE)

class YtScheduleBG(Daemon):
  is_daemon=False
  def __init__(self, *args, **kwargs):
    Daemon.__init__(self, *args, **kwargs)
    self.__class__.__name__ = os.path.basename(sys.argv[0])
    django.setup()

  def run(self): #Define what tasks/processes to daemonize
    '''
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', 
                        filename=os.path.join(rundir, "testdaemon.log"), 
                        level=logging.DEBUG)
    '''
    if self.is_daemon:
      logger = logging.getLogger()
      handler = logging.FileHandler(filename=os.path.join(rundir, "central_background.log"), mode='a' )
      formatter = LogstashFormatterV1()

      handler.setFormatter(formatter)
      logger.addHandler(handler)
    else:
      logger = logging.getLogger()
      handler = logging.StreamHandler(sys.stdout)
      formatter = logging.Formatter('%(levelname)s - %(message)s')

      handler.setFormatter(formatter)
      logger.addHandler(handler)
      logger.setLevel(logging.DEBUG)
    self.work_loop()

  def work_loop(self):
    while True:
      logging.debug("Debug message")
      logging.info("Info message")
      logging.warn("Warning message")
      logging.error("Error message (%s)" % datetime.datetime.now())
      
      loop_start = datetime.datetime.now(tz)
      self.work()
      nexttime = loop_start+datetime.timedelta(seconds=SLEEP_TIME)
      diff = (nexttime - loop_start).total_seconds()
      logging.debug("Now: %s, Target: %s, Diff: %s" % (loop_start, nexttime, diff))
      if diff > 0:
        time.sleep( diff )
  
  def work(self):
    print "background"
  
  def process_cmd(self, argv):
    if len(argv) == 2:
      if 'start' == argv[1]:
        self.is_daemon = True
        self.start()
      elif 'stop' == argv[1]:
        self.stop()
      elif 'restart' == argv[1]:
        self.restart()
      elif 'status' == argv[1]:
        self.status()
      elif 'run' == argv[1]:
        self.run()
      else:
        sys.stdout.write("Unknown command\n")
        sys.exit(2)
      sys.exit(0)
    else:
      sys.stdout.write("Usage: %s start|stop|restart|status\n" % argv[0])
      sys.exit(2)
