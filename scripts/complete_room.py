from room.models import *

def run(*args):
    if len(args) > 0:
        room = Room.objects.get(id=args[0])
    else:
        room = Room.objects.first()

    print("Found Room: %s with state(%s)" % (room.title,room.state))
    print("Stream State=[%s]" % room.check_state())
    print(YouTube.broadcast_status(room.broadcast_id))
    print(room.set_complete())
