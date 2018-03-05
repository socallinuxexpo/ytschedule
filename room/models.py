from django.db import models
import logging
import datetime
import httplib2
import subprocess
import yaml
import pytz
import pprint
from wakeonlan import wol
from django_fsm import FSMField, transition
from django.core.exceptions import ValidationError

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow


logger = logging.getLogger(__name__)
# This OAuth 2.0 access scope allows for read-only access to the authenticated
# user's account, but not other types of account access.
YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
MISSING_CLIENT_SECRETS_MESSAGE="missing client secret file."

class YouTube(object):
  @staticmethod
  def get_authenticated_service(init=False):
    flow = flow_from_clientsecrets("application_secrets.json",
      scope=YOUTUBE_READ_WRITE_SCOPE,
      message=MISSING_CLIENT_SECRETS_MESSAGE)

    storage = Storage("user_oauth2.json")
    credentials = storage.get()
    if init and (credentials is None or credentials.invalid):
      args = argparser.parse_args(["--noauth_local_webserver"])
      credentials = run_flow(flow, storage, args)

    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
      http=credentials.authorize(httplib2.Http()))
  @staticmethod
  def lt(datetime):
    #return pytz.timezone('America/Los_Angeles').localize(datetime)
    return datetime.astimezone(pytz.timezone('America/Los_Angeles') )
   #Bind the broadcast to the video stream. By doing so, you link the video that
   # you will transmit to YouTube to the broadcast that the video is for.
  @staticmethod
  def bind_broadcast(broadcast_id, stream_id):
    bind_broadcast_response = YouTube.get_authenticated_service().liveBroadcasts().bind(
      part="id,contentDetails",
      id=broadcast_id,
      streamId=stream_id
    ).execute()
  @staticmethod
  def broadcast_status(broadcast_id):
    status_response = YouTube.get_authenticated_service().liveBroadcasts().list(
      part="id,status",
      id=broadcast_id,
    ).execute()
    return status_response['items'][0]['status']['lifeCycleStatus']
  @staticmethod
  def set_broadcast_status(broadcast_id, status):
    status_response = YouTube.get_authenticated_service().liveBroadcasts().transition(
      part="id,status",
      id=broadcast_id,
      broadcastStatus=status
    ).execute()
    return status_response

  @staticmethod
  def list_broadcast(status):
    # Status Must be active, all, completed, or upcoming
    response = YouTube.get_authenticated_service().liveBroadcasts().list(
        part="id,status",
        broadcastStatus=status,
        maxResults=50
      ).execute()
    return response

  @staticmethod
  def list_stream_health():
    response = YouTube.get_authenticated_service().liveStreams().list(
        part="id,snippet,status",
        mine=True,
        maxResults=50
      ).execute()
    print "here---------------"
    results = []
    for stream in response.get("items", []):
      results.append({'name': stream["snippet"]["title"],
                      'status': stream["status"]["streamStatus"],
                      'health': stream["status"]["healthStatus"]['status']})
    results.sort();                    
    return results

  @staticmethod
  def check_host_up(hostname):
    try:
      from subprocess import DEVNULL # py3k
    except ImportError:
      import os
      DEVNULL = open(os.devnull, 'wb')

    response = subprocess.call(["ping", "-c", "1", hostname], stdout=DEVNULL, stderr=subprocess.STDOUT)
    if response == 0:
      logger.info('%s is up!', hostname)
    else:
     logger.info('%s is down!', hostname)
    return response

  @staticmethod
  def wake_host_up(mac):
    logger.info("Sending WOL to %s", mac)
    wol.send_magic_packet(mac)

  @staticmethod
  def set_default_video_info(broadcast):
    youtube = YouTube.get_authenticated_service()
    video = youtube.videos().list(
              part="snippet,status,recordingDetails",
              id=broadcast.broadcast_id
            ).execute()['items'][0]
    video['status']['license'] = 'creativeCommon'
    video['status']['embeddable'] = True
    video['snippet']['categoryId'] = 28
    video['snippet']['defaultLanguage'] = 'en'

    if 'recordingDetails' not in video.keys():
      video['recordingDetails'] = dict()
    if 'location' not in video['recordingDetails']:
      video['recordingDetails']['location'] = dict()

    video['recordingDetails']['location']['altitude'] = 260
    video['recordingDetails']['location']['latitude'] = 34.143823
    video['recordingDetails']['location']['longitude'] = -118.144149
    video['recordingDetails']['recordingDate'] = broadcast.start_time.strftime('%Y-%m-%dT00:00:00.000Z')

    update_result = youtube.videos().update(
              part="snippet,status,recordingDetails",
              body=video
            ).execute()

  @staticmethod
  def list_streams(search_by={}):
    youtube = YouTube.get_authenticated_service()
    search = {
        'part': "id,snippet,cdn,status",
        'mine': True,
        'maxResults': 50
    }
    if search_by != {}:
      search.update(search_by)
    list_streams_request = youtube.liveStreams().list( **search )
    streams = []
    while list_streams_request:
      list_streams_response = list_streams_request.execute()

      for stream in list_streams_response.get("items", []):
        streams.append(stream)

      list_streams_request = youtube.liveStreams().list_next(
        list_streams_request, list_streams_response)
    return streams

  @staticmethod
  def find_stream_by_title(title):
    streams = YouTube.list_streams()
    count = 0
    for stream in streams:
      if stream['snippet']['title'] == title:
        break
      count += 1
    if count < len(streams):
      return stream
    return None
  @staticmethod
  def runcmd(command):
    retcode = 1
    try:
      logging.debug("Executing: [%s]"%command)
      #retcode = call(command, shell=True)
      if retcode < 0:
        logging.error("Child was terminated by signal %i" % -retcode)
      else:
        logging.info("Child returned %i" % retcode)
    except OSError as e:
      logging.error("Execution failed: %s" % e)
      return True
    return False

class Room(models.Model):
  states = (('error', 'Error'), ('planned', 'Planned'), ('stream_created', 'Stream Created'), ('published', 'Published'), ('testing', 'Testing'), ('live', 'Live'), ('complete', 'Complete'))
  transitions = [
      { 'trigger': 'publish', 'source': 'planned', 'dest': 'ready', 'before': 'check_stream', 'after': 'after_state' }
  ]
  formats = (("1080p", "1080p"), ("1080p_hfr", "1080p_hfr"), ("720p", "720p"), ("720_hfr", "720p_hfr"), ("480p", "480p"), ("360p", "360p"), ("240p", "240p") )

  title = models.CharField(max_length=128)
  name = models.CharField(max_length=64, blank=True)
  description = models.TextField(max_length=5000, blank=True)
  start_time =  models.DateTimeField('start time')
  end_time = models.DateTimeField('end time')
  state = FSMField(default='planned')
  pub_date = models.DateTimeField('date published', default=datetime.datetime.now, blank=True)

  broadcast_id = models.CharField(max_length=64, default="", blank=True)
  youtube_id = models.CharField(max_length=64, default="", blank=True)
  cdn_format = models.CharField(max_length=15, choices=formats, default="1080p")
  stream_name = models.CharField(max_length=45, default="", blank=True)
  ingestion_address = models.CharField(max_length=128, default="", blank=True)
  backup_address = models.CharField(max_length=128, default="", blank=True)
  is_streaming = models.BooleanField(default=True)
  hostname = models.CharField(max_length=128, default="", blank=True)
  mac_address = models.CharField(max_length=64, default="", blank=True)

  def __init__(self, *args, **kwargs):
    models.Model.__init__(self, *args, **kwargs)
    logger.debug("Room init called")

  def dnsname(self):
    return self.name.lower().replace(" ", "-")

  def cam_name(self):
    return "%s-cam.scaleav.us" % self.dnsname()

  def podium_name(self):
    return "%s-podium.scaleav.us" % self.dnsname()

  def clean(self):
    # start before end
    if self.start_time >= self.end_time:
      raise ValidationError(('Must Start before End and have length.'))

  def can_publish(instance):
    if instance.state == "stream_created":
      return True
    else:
      return False

  @transition(field=state, source='stream_created', target='published', conditions=[can_publish])
  def publish(self):
    logger.debug("Creating Live Broadcast for Room %s" % self.title)
    try:
      youtube = YouTube.get_authenticated_service()
      insert_broadcast_response = youtube.liveBroadcasts().insert(
        part="snippet,status",
        body=dict(
          snippet=dict(
            title=self.title,
            scheduledStartTime=self.start_time.isoformat(),
            scheduledEndTime=self.end_time.isoformat(),
            description=self.description,
          ),
          status=dict(
            #privacyStatus='public' #public, private, or unlisted
            privacyStatus='unlisted' #public, private, or unlisted
          )
        )
      ).execute()

      snippet = insert_broadcast_response["snippet"]

      logger.info("Broadcast '%s' with title '%s' was published at '%s'." % (
         insert_broadcast_response["id"], snippet["title"], snippet["publishedAt"]) )

      logger.debug(insert_broadcast_response)
      self.broadcast_id = insert_broadcast_response["id"]
      self.pub_date = snippet["publishedAt"]

      YouTube.set_default_video_info(self)
      YouTube.bind_broadcast(self.broadcast_id, self.youtube_id)
      self.state = 'published'
      self.save()
    except HttpError, e:
      logger.error( "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
      self.state = 'error'
      self.save()

  @transition(field=state, source=['live', 'error'], target='published')
  def republish(self):
    logger.debug("Creating Live Broadcast for Room %s" % self.title)
    print datetime.datetime.now().isoformat()
    print (datetime.datetime.now()+datetime.timedelta(0,60)).isoformat()
    try:
      youtube = YouTube.get_authenticated_service()
      insert_broadcast_response = youtube.liveBroadcasts().insert(
        part="snippet,status",
        body=dict(
          snippet=dict(
            title=self.title,
            scheduledStartTime=self.start_time.isoformat(),
            scheduledEndTime=self.end_time.isoformat(),
            description=self.description,
          ),
          status=dict(
            privacyStatus='public' #public, private, or unlisted
          )
        )
      ).execute()

      snippet = insert_broadcast_response["snippet"]

      logger.info("Broadcast '%s' with title '%s' was published at '%s'." % (
         insert_broadcast_response["id"], snippet["title"], snippet["publishedAt"]) )

      logger.debug(insert_broadcast_response)
      self.broadcast_id = insert_broadcast_response["id"]
      self.pub_date = snippet["publishedAt"]

      YouTube.set_default_video_info(self)
      YouTube.bind_broadcast(self.broadcast_id, self.youtube_id)
      self.state = 'published'
      self.save()
    except HttpError, e:
      logger.error( "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
      self.state = 'error'
      self.save()

  def can_create(instance):
    if instance.state == "planned":
      return True
    else:
      return False

  @transition(field=state, source='planned', target='stream_created', conditions=[can_create])
  def set_stream(self, stream):
    self.youtube_id = stream['id']
    self.stream_name = stream['cdn']['ingestionInfo']['streamName']
    self.ingestion_address = stream['cdn']['ingestionInfo']['ingestionAddress']
    self.backup_address = stream['cdn']['ingestionInfo']['backupIngestionAddress']

    logger.info("Stream '%s' with title '%s' was created." % (
        stream["id"], stream['snippet']["title"]))
    logger.debug(stream)
    self.state = 'stream_created'
    self.save()

  @transition(field=state, source='planned', target='stream_created', conditions=[can_create])
  def create_stream(self, check=True):
    logger.debug("Creating stream for %s" % self.title)
    if check:
      stream = YouTube.find_stream_by_title("%s_%s" %(self.dnsname(), self.cdn_format))
      if stream == None:
        try:
          youtube = YouTube.get_authenticated_service()
          stream = youtube.liveStreams().insert(
            part="snippet,cdn",
              body=dict(
                snippet=dict(
                  title="%s_%s" %(self.dnsname(), self.cdn_format),
                  description=self.title
              ),
              cdn=dict(
                format=self.cdn_format,
                ingestionType="rtmp"
              )
            )
          ).execute()
        except HttpError, e:
          logger.error( "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content) )
          self.state = 'error'
          self.save()
    self.set_stream(stream)

  def check_stream(self):
    logger.debug( "Checking Stream Status Internal=%s"%self.state )
    youtube = YouTube.get_authenticated_service()
    result = youtube.liveStreams().list(
      part="id,snippet,cdn,status",
      id=self.youtube_id
    ).execute()
    logger.debug( "Checking Stream Status Youtube=%s"% result['items'][0]['status']['streamStatus'] )
    return result['items'][0]

  def check_state(self):
    return self.check_stream()['status']['streamStatus']

  def stream_active(self):
    status = self.check_stream()['status']['healthStatus']['status']
    if status == "good" or status == "ok":
      return True
    else:
      return False

  @transition(field=state, source='published', target='testing', conditions=[stream_active])
  def set_testing(self):
    if self.stream_active():
      status_response = YouTube.set_broadcast_status(self.broadcast_id, 'testing')
      self.state = 'testing'
      self.save()
    else:
      logger.error("Stream [%s] is not ready!" % self.youtube_id)


  @transition(field=state, source=['testing','published'], target='live', conditions=[stream_active])
  def set_live(self):
    if self.stream_active():
      status_response = YouTube.set_broadcast_status(self.broadcast_id, 'live')
      self.state = 'live'
      self.save()
    else:
      logger.error("Stream [%s] is not ready!" % self.youtube_id)

  @transition(field=state, source=['testing','live','published','error'], target='complete')
  def set_complete(self):
    status_response = YouTube.set_broadcast_status(self.broadcast_id, 'complete')
    self.state = 'complete'
    self.save()

  def start_stream(self):
    print "start stream"
    test = subprocess.call("exit 1", shell=True)
    print test
  def __unicode__(self):
    return self.title

  def update_description(self):
    talks = Talk.objects.filter(room=self)
    desc = "SCaLE is the largest community-run open-source and free software conference in North America. It is held annually in Los Angeles.\n"
    for talk in talks:
      diff=(talk.start_time-self.start_time).seconds
      diff += 300

      link="#t="
      hours = diff/3600
      if hours > 0:
        link+="%ih" % hours
      minutes=diff%3600/60
      if minutes > 0:
        link+="%im" % minutes
      seconds = (diff%3600)%60
      if seconds > 0:
        link += "%is" % seconds
      desc += "%s to %s: %s: %s \n" % (YouTube.lt(talk.start_time).strftime('%I:%M %p'),
                                                       YouTube.lt(talk.end_time).strftime('%I:%M %p %Z'),
                                                       talk.title, talk.talk_url)
    desc += "Southern Californa Linux Expo: https://www.socallinuxexpo.org/scale/14x\n"
    self.description = desc
    self.save()

class Talk(models.Model):
  states = (('created', 'Created'), ('published','Published'), ('testing', 'Testing'), ('live', 'Live'), ('complete', 'Complete'))
  room = models.ForeignKey(Room)
  title= models.CharField(max_length=200)
  description = models.TextField(max_length=1024)
  talk_url = models.CharField(max_length=256, default="", blank=True)
  speaker_name = models.CharField(max_length=64, default="", blank=True)
  speaker_url = models.CharField(max_length=256, default="", blank=True)
  state = FSMField(default='created')
  start_time =  models.DateTimeField('start time')
  end_time = models.DateTimeField('end time')
  pub_date = models.DateTimeField('date published', default=datetime.datetime.now(), blank=True)
  broadcast_id = models.CharField(max_length=64, default="", blank=True)

  def __unicode__(self):
    return self.title

  def clean(self):
    # start before end
    if self.start_time >= self.end_time:
      raise ValidationError(_('Must Start before End and have length.'))

  def publish(self):
    logger.debug("Creating Live Broadcast for Talk %s" % self.title)
    try:
      youtube = YouTube.get_authenticated_service()
      insert_broadcast_response = youtube.liveBroadcasts().insert(
        part="snippet,status",
        body=dict(
          snippet=dict(
            title=self.title,
            scheduledStartTime=self.start_time.isoformat(),
            scheduledEndTime=self.end_time.isoformat(),
            description=self.description,
          ),
          status=dict(
            #privacyStatus='public'
            privacyStatus='unlisted'
          )
        )
      ).execute()

      snippet = insert_broadcast_response["snippet"]

      logger.debug("Talk Broadcast '%s' with title '%s' was published at '%s'." % (
         insert_broadcast_response["id"], snippet["title"], snippet["publishedAt"]) )

      logger.info(insert_broadcast_response)
      self.broadcast_id = insert_broadcast_response["id"]
      self.pub_date = snippet["publishedAt"]
      YouTube.set_default_video_info(self)
      YouTube.bind_broadcast(self.broadcast_id, self.room.youtube_id)
      self.state = "published"
      self.save()
    except HttpError, e:
      logger.error("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
      self.save()

  @transition(field=state, source=['published'], target='testing')
  def set_testing(self):
    if self.room.stream_active():
      status_response = YouTube.set_broadcast_status(self.broadcast_id, 'testing')
      self.state = 'testing'
      self.save()
    else:
      logger.error("Stream [%s] is not ready!" % self.broadcast_id)

  @transition(field=state, source=['testing'], target='live')
  def set_live(self):
    if self.room.stream_active():
      status_response = YouTube.set_broadcast_status(self.broadcast_id, 'live')
      self.state = 'live'
      self.save()
    else:
      logger.error("Stream [%s] is not ready!" % self.broadcast_id)

  @transition(field=state, source=['live'], target='complete')
  def set_complete(self):
    status_response = YouTube.set_broadcast_status(self.broadcast_id, 'complete')
    self.state = 'complete'
    self.save()

class CommonDescription(models.Model):
  link_type = models.CharField(max_length=64, choices=(('room', 'Room'), ('talk', 'Talk')), blank=False)
  link_subtype = models.CharField(max_length=64, choices=(('beginning', 'Beginning'), ('end', 'End')), blank=False)
  description = models.TextField(max_length=1024)

  def __unicode__(self):
    return self.link_type + "_" + self.link_subtype

# Create your models here.
