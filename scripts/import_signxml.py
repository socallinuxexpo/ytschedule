from room.models import *
import datetime
import pytz
import iso8601
from xml.etree.ElementTree import Element, SubElement, dump, parse, tostring, fromstring
import os, sys
import django

TIME_ZONE ='America/Los_Angeles'
tz = pytz.timezone(TIME_ZONE)
from html.parser import HTMLParser

class MyParser(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.start_text=""
        self.end_text=""
    def handle_starttag(self, tag, attrs):
        for attr in attrs:
            if 'date-display-start' in attr:
                for attr2 in attrs:
                    if 'content' in attr2:
                        self.start_text = attr2[1]
            if 'date-display-end' in attr:
                for attr2 in attrs:
                    if 'content' in attr2:
                        self.end_text = attr2[1]
def run(*args):
  logger = logging.getLogger()
  logger.setLevel(logging.WARNING)

  ch = logging.StreamHandler(sys.stdout)
  ch.setLevel(logging.DEBUG)
  formatter = logging.Formatter('%(levelname)s - %(message)s')
  ch.setFormatter(formatter)
  logger.addHandler(ch)

  if len(args) > 0:
    xml_filename = args[0]
  else:
    xml_filename = "example_data/sign.xml"

  if len(args) > 1:
    base_url = args[1]
  else:
    base_url = "https://www.socallinuxexpo.org"

  if not os.path.isfile(xml_filename):
    logger.error("File [{}] does not exist.".format(xml_filename))
    exit(-1)


  root = parse(xml_filename).getroot()
  rooms = {}

  for node in root:
    time_parse = MyParser()
    time_parse.feed(node.findtext("Time"))

    start_time = iso8601.parse_date(time_parse.start_text)
    end_time = iso8601.parse_date(time_parse.end_text)
    roomname = node.findtext("Room")
    comp = "%s %s"%(roomname,start_time.strftime('%A %b. %d - SCaLE 17x'))

    q = Room.objects.filter(title=comp)
    if len(q) == 0:
      logger.debug("not found")
      room_obj = Room(name=roomname, title=comp, start_time=start_time, end_time=end_time)
      room_obj.save()
    else:
      room_obj = q[0]
      logger.debug("found [{}]".format(room_obj))
    #print room.start_time.astimezone(tz)
    # Handle room
    if comp in rooms.keys():
      if rooms[comp]["start"] > start_time:
        rooms[comp]["start"] = start_time
      if rooms[comp]["end"] < end_time:
        rooms[comp]["end"] = end_time
    else:
      rooms[comp] = {"start": start_time, "end": end_time}
    title = node.findtext("Title")
    speaker = node.findtext("Speakers")
    url = u"%s%s" %(base_url, node.findtext("Path"))
    description = u"Talk by %s\n\n%s\nMore info at: %s\n" %(speaker, django.utils.html.strip_tags(node.findtext("Short-abstract")), url)
    topic = node.findtext("Topic")
    q = Talk.objects.filter(title=title)
    if len(q) == 0:
      if topic != "BoFs":
        talk = Talk(room_id=room_obj.id, title=title, start_time=start_time, end_time=end_time)
    else:
      talk = q[0]
      if topic == "BoFs":
        talk.delete()
        print("delete talk: {}".format(talk))
    if topic != "BoFs":
      talk.start_time = start_time
      talk.end_time = end_time
      talk.description = description
      talk.talk_url = url
      talk.speaker_name = node.findtext("Speakers")
      talk.save()

  print("Updating Rooms: ")
  for room in rooms:
    print("{}: {} <--> {}".format(room, rooms[room]["start"], rooms[room]["end"]))
    room_obj = Room.objects.filter(title=room)[0]
    room_obj.start_time=rooms[room]["start"]
    room_obj.end_time=rooms[room]["end"]
    room_obj.save()
