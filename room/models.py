from django.db import models
import logging
import datetime
import httplib2
import subprocess
import yaml
import pytz
from django_fsm import FSMField, transition
from django.core.exceptions import ValidationError

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow


#{u'status': {u'streamStatus': u'ready'}, u'kind': u'youtube#liveStream', u'cdn': {u'ingestionType': u'rtmp', u'ingestionInfo': {u'ingestionAddress': u'rtmp://a.rtmp.youtube.com/live2', u'streamName': u'mproctor13.vsg0-jkj1-u1wd-ezu8', u'backupIngestionAddress': u'rtmp://b.rtmp.youtube.com/live2?backup=1'}, u'format': u'1080p'}, u'snippet': {u'channelId': u'UCG7ZLjldwOhB9gc8w78DtfQ', u'description': u'', u'publishedAt': u'2015-08-17T09:33:34.000Z', u'title': u'TestStream1'}, u'etag': u'"dc9DtKVuP_z_ZIF9BZmHcN8kvWQ/QBcAWBG7gKDWZozSDmO1ITLEzeI"', u'id': u'G7ZLjldwOhB9gc8w78DtfQ1439804014774006'}

logger = logging.getLogger(__name__)
CLIENT_SECRETS_FILE = "client_secrets.json"

# This OAuth 2.0 access scope allows for read-only access to the authenticated
# user's account, but not other types of account access.
YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
MISSING_CLIENT_SECRETS_MESSAGE=""

class YouTube(object):
  @staticmethod
  def get_authenticated_service():
    args = {'auth_host_name':'localhost', 'auth_host_port':[8080, 8090], 'logging_level':'ERROR', 'noauth_local_webserver':False}
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
      scope=YOUTUBE_READ_WRITE_SCOPE,
      message=MISSING_CLIENT_SECRETS_MESSAGE)

    storage = Storage("yt_api_oauth2.json")
    credentials = storage.get()
    print credentials

#    if credentials is None or credentials.invalid:
#      credentials = run_flow(flow, storage, args)

    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
      http=credentials.authorize(httplib2.Http()))
  @staticmethod
  def lt(datetime):
    #return pytz.timezone('America/Los_Angeles').localize(datetime)
    return datetime.astimezone(pytz.timezone('America/Los_Angeles') )


class Room(models.Model):
  states = (('error', 'Error'), ('planned', 'Planned'), ('created', 'Created'), ('ready', 'Ready'), ('inactive', 'Inactive'), ('active', 'Active'))
  transitions = [
      { 'trigger': 'publish', 'source': 'planned', 'dest': 'ready', 'before': 'check_stream', 'after': 'after_state' }
  ]
  formats = (("1080p", "1080p"), ("1080p_hfr", "1080p_hfr"), ("720p", "720p"), ("720_hfr", "720p_hfr"), ("480p", "480p"), ("360p", "360p"), ("240p", "240p") )
  
  name = models.CharField(max_length=64)
  title= models.CharField(max_length=200)
  description = models.TextField(max_length=1024)
  start_time =  models.DateTimeField('start time')
  end_time = models.DateTimeField('end time')
  #state = models.CharField(max_length=64, choices=states, default='planned')
  state = FSMField(default='planned')
  pub_date = models.DateTimeField('date published', default=datetime.datetime.now(), blank=True)

  ytid = models.CharField(max_length=64, default="", blank=True)
  cdn_format = models.CharField(max_length=15, choices=formats, default="1080p")
  stream_name = models.CharField(max_length=45, default="", blank=True)
  ingestion_address = models.CharField(max_length=128, default="", blank=True)
  backup_address = models.CharField(max_length=128, default="", blank=True)

  def __init__(self, *args, **kwargs):
    models.Model.__init__(self, *args, **kwargs)
    logger.debug("Room init called")

  def clean(self):
    # start before end
    if self.start_time >= self.end_time:
      raise ValidationError(('Must Start before End and have length.'))

  def can_publish(instance):
    if instance.state == "planned":
      return True
    else:
      return False

  @transition(field=state, source='planned', target='created', conditions=[can_publish])
  def publish_stream(self):
    logger.debug("Creating stream for %s" % self.title)
    try:
      youtube = YouTube.get_authenticated_service()
      insert_stream_response = youtube.liveStreams().insert(
        part="snippet,cdn",
          body=dict(
            snippet=dict(
              title=self.title,
              description=self.description
          ),
          cdn=dict(
            format=self.cdn_format,
            ingestionType="rtmp"
          )
       )
      ).execute()
      
      self.ytid = insert_stream_response['id']
      self.stream_name = insert_stream_response['cdn']['ingestionInfo']['streamName']
      self.ingestion_address = insert_stream_response['cdn']['ingestionInfo']['ingestionAddress']
      self.backup_address = insert_stream_response['cdn']['ingestionInfo']['backupIngestionAddress']

      logger.debug("Stream '%s' with title '%s' was created." % (
        insert_stream_response["id"], insert_stream_response['snippet']["title"]))
      print insert_stream_response
      self.state = 'created'
      self.save()
    except HttpError, e:
      print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
      self.state = 'error'
      self.save()
  
  def check_stream(self):
    print "checking stream %s"%self.state
    youtube = YouTube.get_authenticated_service()
    result = youtube.liveStreams().list(
      part="id,snippet,cdn,status",
      id=self.ytid
    ).execute()
    return result['items'][0]
  def check_state(self):
    return self.check_stream()['status']['streamStatus']
  
  @transition(field=state, source='created', target='ready')
  def is_ready(self):
    status = self.check_stream()
    print "Stream %s is %s"%(self.title, status['status']['streamStatus'])
    self.state = status['status']['streamStatus']
    self.save()
    
  
  @transition(field=state, source='ready', target='active')
  def stream(self):
    print "start stream"
    test = subprocess.call("exit 1", shell=True)
    print test
  

  def __str__(self):
    return self.name

class Talk(models.Model):
  states = (('revoked', 'Revoked'), ('reclaimed', 'Reclaimed'), ('abandoned', 'Abandoned'), ('created', 'Created'), ('ready','Ready'), ('testStarting', 'TestStarting'), ('testing', 'Testing'), ('liveStarting', 'LiveStarting'), ('live', 'Live'), ('complete', 'Complete'))
  room = models.ForeignKey(Room) 
  name = models.CharField(max_length=64)
  title= models.CharField(max_length=200)
  description = models.TextField(max_length=1024)
  talk_url = models.CharField(max_length=256, default="", blank=True)
  speaker_name = models.CharField(max_length=64, default="", blank=True)
  speaker_url = models.CharField(max_length=256, default="", blank=True)
  state = models.CharField(max_length=64, choices=states, default='created')
  start_time =  models.DateTimeField('start time')
  end_time = models.DateTimeField('end time')
  pub_date = models.DateTimeField('date published', default=datetime.datetime.now(), blank=True)
  
  def __str__(self):
    return self.name
  
  def clean(self):
    # start before end
    if self.start_time >= self.end_time:
      raise ValidationError(_('Must Start before End and have length.'))


# Create your models here.
