from room.models import *
import time

TIME_ZONE ='America/Los_Angeles'
tz = pytz.timezone(TIME_ZONE)
logging.basicConfig(level=logging.DEBUG)

def run(*args):
    tz = pytz.timezone(TIME_ZONE)
    time.tzset()
    os.environ['TZ'] = 'America/Los_Angeles'

    rooms = []
    logger.debug("Args[0]=[{}]".format(args[0]))
    if len(args) >= 1:
        if args[0].lower() == "all":
            rooms = Room.objects.all()
        else:
            rooms.append( Room.objects.get(id=args[0]) )
    else:
        rooms.append(Room.objects.first())
    privacy = "unlisted"

    for room in rooms:
        # room.update_description()
        logger.info("[%i]%s -- %s" % (room.id, room.title, room.state))
        if room.state == "planned":
            room.create_stream()
            logger.info("Room {} Stream Created.".format(room.id))
        room.publish(privacy)

    #    talks = Talk.objects.filter(room=room)
    #    for talk in talks:
    #      talk.publish()
