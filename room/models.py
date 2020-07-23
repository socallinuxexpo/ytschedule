from django.db import models
import logging
import datetime
import httplib2
import subprocess
import os
import sys
import pprint
import pytz
import wakeonlan as wol
from django_fsm import FSMField, transition
from django.core.exceptions import ValidationError

# from apiclient.discovery import build
# from apiclient.errors import HttpError
# from oauth2client.client import flow_from_clientsecrets
# from oauth2client.file import Storage
# from oauth2client.tools import argparser, run_flow

import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow

from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets
from oauth2client.tools import argparser, run_flow


logger = logging.getLogger(__name__)
# This OAuth 2.0 access scope allows for read-only access to the authenticated
# user's account, but not other types of account access.
# YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
# YOUTUBE_API_SERVICE_NAME = "youtube"
# YOUTUBE_API_VERSION = "v3"
# MISSING_CLIENT_SECRETS_MESSAGE="missing client secret file."
CLIENT_SECRETS_FILE = 'client_secret.json'
SCOPES = ['https://www.googleapis.com/auth/youtube']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
# Helpful message to display if the CLIENT_SECRETS_FILE is missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0
To make this sample run you will need to populate the client_secrets.json file
found at:
   %s
with information from the Developers Console
https://console.developers.google.com
For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))

class YouTube(object):
    @staticmethod
    # Authorize the request and store authorization credentials.
    def get_authenticated_service_new():
        flow = InstalledAppFlow.from_client_secrets_file(
            CLIENT_SECRETS_FILE, SCOPES)
        credentials = flow.run_console()
        return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
    def get_authenticated_service(init=False):
        flow = flow_from_clientsecrets("application_secrets.json",
                                       scope=SCOPES,
                                       message=MISSING_CLIENT_SECRETS_MESSAGE)

        storage = Storage("user_oauth2.json")
        credentials = storage.get()
        if init and (credentials is None or credentials.invalid):
            args = argparser.parse_args(["--noauth_local_webserver"])
            credentials = run_flow(flow, storage, args)

        return build(API_SERVICE_NAME, API_VERSION,
                     http=credentials.authorize(httplib2.Http()))
    @staticmethod
    def lt(datetime):
        # return pytz.timezone('America/Los_Angeles').localize(datetime)
        return datetime.astimezone(pytz.timezone('America/Los_Angeles'))

    # Bind the broadcast to the video stream. By doing so, you link the video
    # that you will transmit to YouTube to the broadcast that the video is for.
    @staticmethod
    def bind_broadcast(broadcast_id, stream_id):
        bind_broadcast_response = YouTube.get_authenticated_service(
        ).liveBroadcasts().bind(
            part="id,contentDetails",
            id=broadcast_id,
            streamId=stream_id).execute()

    @staticmethod
    def broadcast_status(broadcast_id):
        status_response = YouTube.get_authenticated_service(
        ).liveBroadcasts().list(
            part="id,status",
            id=broadcast_id,).execute()
        return status_response['items'][0]['status']['lifeCycleStatus']

    @staticmethod
    def set_broadcast_status(broadcast_id, status):
        status_response = YouTube.get_authenticated_service(
        ).liveBroadcasts().transition(
            part="id,status",
            id=broadcast_id,
            broadcastStatus=status).execute()
        return status_response

    @staticmethod
    def list_broadcast(status):
        # Status Must be active, all, completed, or upcoming
        response = YouTube.get_authenticated_service().liveBroadcasts().list(
            part="id,status",
            broadcastStatus=status,
            maxResults=50).execute()
        return response

    @staticmethod
    def check_channel():
        # Status Must be active, all, completed, or upcoming
        response = YouTube.get_authenticated_service().channels().list(
          mine=True,
          part="snippet"
        ).execute()
        return response

    @staticmethod
    def list_stream_health():
        logger.info("---------------Calling YouTube---------------")
        response = YouTube.get_authenticated_service().liveStreams().list(
            part="id,snippet,status",
            mine=True,
            maxResults=50).execute()
        results = []
        for stream in response.get("items", []):
            results.append({
                'name': stream["snippet"]["title"],
                'status': stream["status"]["streamStatus"],
                'health': stream["status"]["healthStatus"]['status']
            })
            # results.sort()
        return results

    @staticmethod
    def check_host_up(hostname):
        try:
            from subprocess import DEVNULL  # py3k
        except ImportError:
            import os
        DEVNULL = open(os.devnull, 'wb')

        response = subprocess.call(
            ["ping", "-c", "1", hostname],
            stdout=DEVNULL,
            stderr=subprocess.STDOUT)
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
            id=broadcast.broadcast_id).execute()['items'][0]
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
        video['recordingDetails']['recordingDate'] = \
            broadcast.start_time.strftime('%Y-%m-%dT00:00:00.000Z')

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
        list_streams_request = youtube.liveStreams().list(**search)
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
            logging.debug("Executing: [%s]" % command)
            retcode = subprocess.call(command, shell=True)
            if retcode < 0:
                logging.error("Child was terminated by signal %i" % -retcode)
            else:
                logging.info("Child returned %i" % retcode)
        except OSError as e:
            logging.error("Execution failed: %s" % e)
            return True
        return False

    @staticmethod
    def unlock_service(service_name):
        # open("/etc/init/{}.override".format(service_name), 'w').close()
        cammand = "echo '' | sudo tee /etc/init/{}.override > /dev/null".format(service_name)
        YouTube.runcmd(cammand)

    @staticmethod
    def lock_service(service_name):
        # open("/etc/init/{}.override".format(service_name), 'w').write("manual").close()
        cammand = "echo manual | sudo tee /etc/init/{}.override > /dev/null".format(service_name)

    @staticmethod
    def run_service(service_name, arg):
        # open("/etc/init/{}.override".format(service_name), 'w').write("manual").close()
        cammand = "sudo service {} {}".format(service_name, arg)
        YouTube.runcmd(cammand)


class Room(models.Model):
    states = (('error', 'Error'),
              ('planned', 'Planned'),
              ('stream_created', 'Stream Created'),
              ('published', 'Published'),
              ('testing', 'Testing'),
              ('live', 'Live'),
              ('complete', 'Complete'))
    transitions = [
        {'trigger': 'publish',
         'source': 'planned',
         'dest': 'ready',
         'before': 'check_stream',
         'after': 'after_state'}
    ]
    formats = (("1080p", "1080p"),
               ("1080p_hfr", "1080p_hfr"),
               ("720p", "720p"),
               ("720_hfr", "720p_hfr"),
               ("480p", "480p"),
               ("360p", "360p"),
               ("240p", "240p"))

    title = models.CharField(max_length=128)
    name = models.CharField(max_length=64, blank=True)
    description = models.TextField(max_length=5000, blank=True)
    start_time = models.DateTimeField('start time')
    end_time = models.DateTimeField('end time')
    state = FSMField(default='planned')
    pub_date = models.DateTimeField(
        'date published',
        default=datetime.datetime.now,
        blank=True)

    broadcast_id = models.CharField(max_length=64, default="", blank=True)
    youtube_id = models.CharField(max_length=64, default="", blank=True)
    cdn_format = models.CharField(
        max_length=15,
        choices=formats,
        default="1080p")
    stream_name = models.CharField(max_length=45, default="", blank=True)
    ingestion_address = models.CharField(
        max_length=128,
        default="",
        blank=True)
    backup_address = models.CharField(max_length=128, default="", blank=True)
    is_streaming = models.BooleanField(default=True)
    hostname = models.CharField(max_length=128, default="", blank=True)
    mac_address = models.CharField(max_length=64, default="", blank=True)
    is_dual_stream = models.BooleanField(default=False)
    save_camera = models.BooleanField(default=False)

    def __init__(self, *args, **kwargs):
        models.Model.__init__(self, *args, **kwargs)
        logger.debug("Room init called")

    def __str__(self):
        return self.title

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

    @transition(field=state, source='stream_created',
                target='published', conditions=[can_publish])
    def publish(self, privacy="unlisted"):
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
                        description=self.complete_description(),
                    ),
                    status=dict(
                        privacyStatus=privacy  # public, private, or unlisted
                    )
                )
            ).execute()

            snippet = insert_broadcast_response["snippet"]

            logger.info("Broadcast '%s' with title '%s' was published at '%s'."
                        % (insert_broadcast_response["id"],
                           snippet["title"],
                           snippet["publishedAt"]))

            logger.debug(insert_broadcast_response)
            self.broadcast_id = insert_broadcast_response["id"]
            self.pub_date = snippet["publishedAt"]

            YouTube.set_default_video_info(self)
            YouTube.bind_broadcast(self.broadcast_id, self.youtube_id)
            self.state = 'published'
            self.save()
        except HttpError as e:
            logger.error("An HTTP error %d occurred:\n%s" %
                         (e.resp.status, e.content))
            self.state = 'error'
            self.save()

    @transition(field=state,
                source=['live', 'error', 'published'],
                target='published')
    def republish(self):
        logger.debug("Creating Live Broadcast for Room %s" % self.title)
        print(datetime.datetime.now().isoformat())
        print((datetime.datetime.now()+datetime.timedelta(0, 60)).isoformat())
        try:
            youtube = YouTube.get_authenticated_service()
            insert_broadcast_response = youtube.liveBroadcasts().insert(
                part="snippet,status",
                body=dict(
                    snippet=dict(
                        title=self.title,
                        scheduledStartTime=self.start_time.isoformat(),
                        scheduledEndTime=self.end_time.isoformat(),
                        description=self.complete_description(),
                    ),
                    status=dict(
                        privacyStatus='public'  # public, private, or unlisted
                    )
                )
            ).execute()

            snippet = insert_broadcast_response["snippet"]

            logger.info("Broadcast '%s' with title '%s' was published at '%s'."
                        % (insert_broadcast_response["id"], snippet["title"],
                           snippet["publishedAt"]))

            logger.debug(insert_broadcast_response)
            self.broadcast_id = insert_broadcast_response["id"]
            self.pub_date = snippet["publishedAt"]

            YouTube.set_default_video_info(self)
            YouTube.bind_broadcast(self.broadcast_id, self.youtube_id)
            self.state = 'published'
        except HttpError as e:
            logger.error("An HTTP error %d occurred:\n%s" %
                         (e.resp.status, e.content))
            self.state = 'error'
        self.save()

    def can_create(instance):
        if instance.state == "planned":
            return True
        else:
            return False

    @transition(field=state,
                source='planned',
                target='stream_created',
                conditions=[can_create])
    def set_stream(self, stream):
        self.youtube_id = stream['id']
        ingestionInfo = stream['cdn']['ingestionInfo']
        self.stream_name = ingestionInfo['streamName']
        self.ingestion_address = ingestionInfo['ingestionAddress']
        self.backup_address = ingestionInfo['backupIngestionAddress']

        logger.info("Stream '%s' with title '%s' was created." % (
            stream["id"], stream['snippet']["title"]))
        logger.debug(stream)
        self.state = 'stream_created'
        self.save()

    @transition(field=state,
                source='planned',
                target='stream_created',
                conditions=[can_create])
    def create_stream(self, check=True):
        logger.debug("Creating stream for %s" % self.title)
        if check:
            stream = YouTube.find_stream_by_title(
                "%s_%s" % (self.dnsname(), self.cdn_format))

        if stream is None:
            try:
                youtube = YouTube.get_authenticated_service()
                stream = youtube.liveStreams().insert(
                    part="snippet,cdn",
                    body=dict(
                        snippet=dict(
                            title="%s_%s" % (self.dnsname(), self.cdn_format),
                            description=self.title
                        ),
                        cdn=dict(
                            format=self.cdn_format,
                            ingestionType="rtmp"
                        )
                    )
                ).execute()
            except HttpError as e:
                logger.error("An HTTP error %d occurred:\n%s" %
                             (e.resp.status, e.content))
                self.state = 'error'
                self.save()
        self.set_stream(stream)

    def check_stream(self):
        logger.debug("Checking Stream Status Internal=%s" % self.state)
        youtube = YouTube.get_authenticated_service()
        result = youtube.liveStreams().list(
            part="id,snippet,cdn,status",
            id=self.youtube_id
        ).execute()
        logger.debug("Checking Stream Status Youtube=%s" %
                     result['items'][0]['status']['streamStatus'])
        return result['items'][0]

    def check_state(self):
        return self.check_stream()['status']['streamStatus']

    def stream_active(self):
        status = self.check_stream()['status']['healthStatus']['status']
        if status == "good" or status == "ok":
            return True
        else:
            return False

    @transition(field=state, source=['published', 'error', 'planned'], target='testing')
    def set_testing_offline(self):
        self.state = 'testing'
        self.save()

    @transition(field=state,
                source='published',
                target='testing',
                conditions=[stream_active])
    def set_testing(self):
        if self.stream_active():
            status_response = YouTube.set_broadcast_status(
                self.broadcast_id, 'testing')
            self.set_testing_offline()
        else:
            logger.error("Stream [%s] is not ready!" % self.youtube_id)

    @transition(field=state,
                source=['testing', 'published'],
                target='live',
                conditions=[stream_active])
    def set_live_offline(self):
       self.state = 'live'
       self.save()

    @transition(field=state,
                source=['testing', 'published'],
                target='live',
                conditions=[stream_active])
    def set_live(self):
        if self.stream_active():
            status_response = YouTube.set_broadcast_status(
                self.broadcast_id, 'live')
            self.set_live_offline()
        else:
            logger.error("Stream [%s] is not ready!" % self.youtube_id)

    @transition(field=state,
                source=['testing', 'live', 'published', 'error'],
                target='complete')
    def set_complete_offline(self):
        self.state = 'complete'
        self.save()

    @transition(field=state,
                source=['testing', 'live', 'published', 'error'],
                target='complete')
    def set_complete(self):
        status_response = YouTube.set_broadcast_status(
            self.broadcast_id, 'complete')
        self.set_complete_offline()

    def start_stream(self):
        print("start stream")
        test = subprocess.call("exit 1", shell=True)
        print(test)

    def __unicode__(self):
        return self.title

    def complete_description(self):
        description = ""
        query = CommonDescription.objects.filter(link_type="room")
        query = query.filter(link_subtype="beginning")
        if len(query) > 0:
          for result in query:
              description += result.description
              description += "\n"
        description += self.description
        description += "\n"
        query = CommonDescription.objects.filter(link_type="room")
        query = query.filter(link_subtype="end")
        if len(query) > 0:
          for result in query:
              description += result.description
              description += "\n"
        return description

    def update_description(self):
        talks = Talk.objects.filter(room=self)
        desc = ""
        # desc = "SCaLE is the largest community-run open-source and free " \
        #        "software conference in North America. It is held annually in" \
        #        " Los Angeles.\n"
        for talk in talks:
            diff = (talk.start_time-self.start_time).seconds
            diff += 300

            link = "#t="
            hours = diff/3600
            if hours > 0:
                link += "%ih" % hours
            minutes = diff % 3600/60
            if minutes > 0:
                link += "%im" % minutes
            seconds = (diff % 3600) % 60
            if seconds > 0:
                link += "%is" % seconds
            desc += "<a href=\"{}\">{}</a> to {}: <a href=\"{}\">{}</a><br/>\n".format(link,
                            YouTube.lt(talk.start_time).strftime('%I:%M %p'),
                            YouTube.lt(talk.end_time).strftime('%I:%M %p %Z'),
                            talk.talk_url, talk.title)
        # desc += "Southern Californa Linux Expo: " \
        #         "https://www.socallinuxexpo.org/scale/16x\n"
        self.description = desc
        self.save()

    def update_description2(self):
        talks = Talk.objects.filter(room=self)
        desc = ""
        # desc = "SCaLE is the largest community-run open-source and free " \
        #        "software conference in North America. It is held annually in" \
        #        " Los Angeles.\n"
        for talk in talks:
            diff = (talk.start_time-self.start_time).seconds
            diff += 300

            link = "#t="
            hours = diff/3600
            if hours > 0:
                link += "%ih" % hours
            minutes = diff % 3600/60
            if minutes > 0:
                link += "%im" % minutes
            seconds = (diff % 3600) % 60
            if seconds > 0:
                link += "%is" % seconds
            desc += "{} to {}: {} {}\n".format(
                            YouTube.lt(talk.start_time).strftime('%I:%M %p'),
                            YouTube.lt(talk.end_time).strftime('%I:%M %p %Z'),
                            talk.title, talk.talk_url)
        # desc += "Southern Californa Linux Expo: " \
        #         "https://www.socallinuxexpo.org/scale/16x\n"
        self.description = desc
        self.save()


class Talk(models.Model):
    states = (('created', 'Created'),
              ('published', 'Published'),
              ('testing', 'Testing'),
              ('live', 'Live'),
              ('complete', 'Complete'))
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=1024)
    talk_url = models.CharField(max_length=256, default="", blank=True)
    speaker_name = models.CharField(max_length=256, default="", blank=True)
    speaker_url = models.CharField(max_length=256, default="", blank=True)
    state = FSMField(default='created')
    start_time = models.DateTimeField('start time')
    end_time = models.DateTimeField('end time')
    pub_date = models.DateTimeField(
        'date published',
        default=datetime.datetime.now(),
        blank=True)
    broadcast_id = models.CharField(max_length=64, default="", blank=True)
    streamable = models.BooleanField(default=True)
    recordable = models.BooleanField(default=True)
    def __unicode__(self):
        return self.title

    def __str__(self):
        return self.title

    def clean(self):
        # start before end
        if self.start_time >= self.end_time:
            raise ValidationError(_('Must Start before End and have "length.'))

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
                        # privacyStatus='public'
                        privacyStatus='unlisted'
                    )
                )
            ).execute()

            snippet = insert_broadcast_response["snippet"]

            logger.debug("Talk Broadcast '%s' with title '%s' "
                         "was published at '%s'." % (
                             insert_broadcast_response["id"],
                             snippet["title"],
                             snippet["publishedAt"]))

            logger.info(insert_broadcast_response)
            self.broadcast_id = insert_broadcast_response["id"]
            self.pub_date = snippet["publishedAt"]
            YouTube.set_default_video_info(self)
            YouTube.bind_broadcast(self.broadcast_id, self.room.youtube_id)
            self.state = "published"
            self.save()
        except HttpError as e:
            logger.error("An HTTP error %d occurred:\n%s" %
                         (e.resp.status, e.content))
            self.save()

    @transition(field=state, source=['published', 'error', 'planned'], target='testing')
    def set_testing_offline(self):
        self.state = 'testing'
        self.save()

    @transition(field=state, source=['published'], target='testing')
    def set_testing(self):
        if self.room.stream_active():
            status_response = YouTube.set_broadcast_status(
                self.broadcast_id,
                'testing')
            self.set_testing_offline()
        else:
            logger.error("Stream [%s] is not ready!" % self.broadcast_id)

    @transition(field=state, source=['testing'], target='live')
    def set_live_offine(self):
        self.state = 'live'
        self.save()
    
    @transition(field=state, source=['testing'], target='live')
    def set_live(self):
        if self.room.stream_active():
            status_response = YouTube.set_broadcast_status(
                self.broadcast_id,
                'live')
            self.set_live_offine()
        else:
            logger.error("Stream [%s] is not ready!" % self.broadcast_id)

    @transition(field=state, source=['live'], target='complete')
    def set_complete_offline(self):
        self.state = 'complete'
        self.save()

    @transition(field=state, source=['live'], target='complete')
    def set_complete(self):
        status_response = YouTube.set_broadcast_status(
            self.broadcast_id,
            'complete')
        self.set_complete_offline()


class CommonDescription(models.Model):
    link_type = models.CharField(
        max_length=64,
        choices=(('room', 'Room'), ('talk', 'Talk')),
        blank=False)
    link_subtype = models.CharField(
        max_length=64,
        choices=(('beginning', 'Beginning'), ('end', 'End')),
        blank=False)
    description = models.TextField(max_length=1024)

    def __unicode__(self):
        return self.link_type + "_" + self.link_subtype

    def __str__(self):
        return self.link_type + "_" + self.link_subtype
