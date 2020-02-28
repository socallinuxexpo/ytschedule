from room.models import *

def run():
    rooms = Room.objects.all()
    print("Found %s Rooms." % len(rooms))
    print("==============================")
    print(rooms[0].complete_description())
    print("==============================")
    rooms[0].update_description()
    print(rooms[0].complete_description())
    print("==============================")
