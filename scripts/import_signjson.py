from room.models import *
import datetime
import pytz
import iso8601
# from xml.etree.ElementTree import Element, SubElement, dump, parse, tostring, fromstring
import json
import os, sys
from bs4 import BeautifulSoup
import django
import emoji

TIME_ZONE ='America/Los_Angeles'
tz = pytz.timezone(TIME_ZONE)
def run(*args):
  logger = logging.getLogger()
  logger.setLevel(logging.WARNING)

  ch = logging.StreamHandler(sys.stdout)
  ch.setLevel(logging.DEBUG)
  formatter = logging.Formatter('%(levelname)s - %(message)s')
  ch.setFormatter(formatter)
  logger.addHandler(ch)
  print(args)
  if len(args) > 0:
    source_filename = args[0]
  else:
    source_filename = "signs.json"

  if len(args) > 1:
    base_url = args[1]
  else:
    base_url = "https://www.socallinuxexpo.org"

  if not os.path.isfile(source_filename):
    logger.error("File [{}] does not exist.".format(source_filename))
    exit(-1)

  rooms = {}
  with open(source_filename, 'r') as file:
    data = json.load(file)
  talks = {'total': len(data), 'talk': 0, 'expo': 0, 'bof': 0, 'other': 0, 'errors': 0}
  # print( len(data) )
  for entry in data:
    try:
      if entry['Location'] == '':
        # pprint.pp(entry)
        print("Unused Entry(blank, location, [%s])"%entry['Name'])
        talks['other']+=1
      elif entry['Location'] == "Expo":
        print("Unused Entry(%s)"%entry['Name'])
        talks['expo']+=1
      elif entry['Topic'] == "BoFs":
        print("Unused Entry(%s)"%entry['Name'])
        talks['bof']+=1
      else:
        start_time = iso8601.parse_date(entry['StartTime'])
        end_time = iso8601.parse_date(entry['EndTime'])
      
        comp = "%s %s"%(entry['Location'],start_time.strftime('%A %b. %d - SCaLE 23x'))

        q = Room.objects.filter(title=comp)
        if len(q) == 0:
          logger.debug("not found")
          room_obj = Room(name=entry['Location'], title=comp, start_time=start_time, end_time=end_time)
          room_obj.save()
        else:
          room_obj = q[0]
          logger.debug("found [{}]".format(room_obj))
        #print room.start_time.astimezone(tz)
        title = emoji.replace_emoji(entry['Name'], replace="")
        speaker = entry['Speakers']
        url = u"%s%s" %(base_url, entry['Link'])
        description = u"Talk by %s\n\n%s\nMore info at: %s\n" %(speaker, django.utils.html.strip_tags(entry['Description'].replace('&nbsp;', ' ')), url)
        
        topic = entry['Topic']
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
          talk.description = emoji.replace_emoji(description, replace="")
          talk.talk_url = url
          talk.speaker_name = speaker
          talk.save()

        # Handle room
        if comp in rooms.keys():
          if rooms[comp]["start"] > start_time:
            rooms[comp]["start"] = start_time
          if rooms[comp]["end"] < end_time:
            rooms[comp]["end"] = end_time
        else:
          rooms[comp] = {"start": start_time, "end": end_time}
        talks['talk']+=1
    except Exception as e:
      print("Had error(%s) with: "%e)
      talks['errors']+=1
  print("Updating Rooms: ")
  for room in rooms:
    # print("{}:\t {}\t <-->\t {}".format(room, rooms[room]["start"], rooms[room]["end"]))
    room_obj = Room.objects.filter(title=room)[0]
    room_obj.start_time=rooms[room]["start"]
    room_obj.end_time=rooms[room]["end"]
    room_obj.save()
    print("{name:15} {day:10} {start:8} <--> {end:8}".format(name=room_obj.name, day=room_obj.start_time.strftime('%A'), start=room_obj.start_time.strftime('%I:%M %p'), end=room_obj.end_time.strftime('%I:%M %p') ))
  print(talks)
  # print( "[%s] == [%s]"%(talks['total'], (talks['talk'] + talks['expo'] + talks['bof'] + talks['other']) ) )
  if(talks['total'] == (talks['talk'] + talks['expo'] + talks['bof'] + talks['other']) ):
    exit(0)
  else:
    exit(-2)
