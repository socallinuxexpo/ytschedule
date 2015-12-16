#!/usr/bin/python
import os, sys

dir = os.path.dirname(__file__)
path = os.path.join(dir, '../ytschedule')
sys.path.append(os.path.join(dir, '../'))
os.environ["DJANGO_SETTINGS_MODULE"] = "ytschedule.settings"

from room.models import *

print len(Room.objects.all())
print len(Talk.objects.all())


