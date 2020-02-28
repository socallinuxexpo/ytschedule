from room.models import *
import time

TIME_ZONE ='America/Los_Angeles'
tz = pytz.timezone(TIME_ZONE)


def run(*args):
    tz = pytz.timezone(TIME_ZONE)
    time.tzset()
    os.environ['TZ'] = 'America/Los_Angeles'

    rooms = []
    print(args[0])
    if len(args) >= 1:
        if args[0].lower() == "all":
            rooms = Room.objects.all()
        else:
            rooms.append( Room.objects.get(id=args[0]) )
    else:
        rooms.append(Room.objects.first())
    privacy = "private"

    for room in rooms:
        print("[%i]%s -- %s" % (room.id, room.title, room.state))
        # room.create_stream()
        # print("Room {} Stream Created.".format(room.id))
        # room.publish(privacy)()
        room.update_description2()
        print("\n\n{}\n\n".format(room.complete_description()))

    #    talks = Talk.objects.filter(room=room)
    #    for talk in talks:
    #      talk.publish()
