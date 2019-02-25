from django.test import TestCase
from ..models import Room
from django.utils import timezone
from datetime import timedelta
#from django.core.urlresolvers import reverse

# models test
class RoomTest(TestCase):
	def create_room(self, roomname="La Jolla",
                    title="This is room Title",
                    start_time=timezone.now(), end_time=timezone.now() + timedelta(hours=7)):
		return Room.objects.create(name=roomname, title=title,
                                   start_time=start_time, end_time=end_time)

	def test_room_creation(self):
		w = self.create_room()
		self.assertTrue(isinstance(w, Room))
		self.assertEqual(w.__unicode__(), w.title)
