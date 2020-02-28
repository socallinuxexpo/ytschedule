from room.models import *
import time

TIME_ZONE ='America/Los_Angeles'
tz = pytz.timezone(TIME_ZONE)


def run(*args):
    tz = pytz.timezone(TIME_ZONE)
    time.tzset()
    os.environ['TZ'] = 'America/Los_Angeles'
  if len(args) > 0:
    days = int(args[0])
  else:
    days = 0

  now = datetime.datetime.now(tz)
  start = datetime.datetime(now.year,now.month,now.day+days)
  end = datetime.datetime(now.year,now.month,now.day+1+days)
  print("%s <==> %s" % (start, end))
  query = Room.objects.filter(Q(state="published") | Q(state="testing") | Q(state="live"))
  query = query.filter(start_time__lte=end)
  query = query.filter(end_time__gte=start)
  streams=0
  if len(query) > 0:
    for result in query:
      print(result)
      streams+=1
      talks = Talk.objects.filter(room=result).order_by('start_time')
      for talk in talks:
          print("--%s--%s" % (talk.start_time, talk))
          streams+=1
  print streams
  # rooms = []
  # if len(args) > 1:
  #   if args[1].lower() == "all":
  #     rooms = Room.objects.all()
  #   else:
  #     rooms.append( Room.objects.get(id=args[1]) )
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
