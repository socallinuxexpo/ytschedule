from room.models import *

def run(*args):

  if len(args) > 1:
    valid_status=['active', 'all', 'completed', 'upcoming']
    if args[1] in valid_status:
      status = args[1]
    else:
      print("Status must be 'active', 'all', 'completed', 'upcoming'")
      exit(1)
  else:
    status = 'all'

  print(YouTube.list_stream_health())

  #results = YouTube.list_broadcast(status)
  #print "Showing %s of %s results." % (len(results['items']), results['pageInfo']['totalResults'])

  #print results['pageInfo']['totalResults']
  #print len(results['items'])
  #for broadcast in results['items']:
  #  print "[%s] video_id=%s" % (broadcast['status']['lifeCycleStatus'], broadcast['id'])
  #pprint.pprint(results)
