import sys, os
from daemon import Daemon
from utils.background import YtScheduleBG
from room.models import *
from django.db.models import Q
import django_fsm

class CenteralBackground(YtScheduleBG):
  def work(self):
    now = datetime.datetime.now(tz)
    query = Room.objects.filter(start_time__lte=now)
    query = query.filter(end_time__gte=now+datetime.timedelta(seconds=10*60))
    if len(query) > 0:
      for result in query:
        print("[%s]: %s -- %s" % (result.title, result.start_time, result.end_time))
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
          print("[%s]: %s -- %s" % (result.title, result.start_time, result.end_time))

if __name__ == "__main__":
    rundir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../run'))
    daemon = CenteralBackground( os.path.join(rundir, "%s.pid" % os.path.basename(__file__)) )
    daemon.process_cmd(sys.argv)
