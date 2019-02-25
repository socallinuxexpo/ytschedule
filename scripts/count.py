from room.models import *

def run():
    print("Found %s Rooms." % len(Room.objects.all()))
    print("Found %s Talks." % len(Talk.objects.all()))
