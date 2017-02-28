# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CommonDescription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('link_type', models.CharField(max_length=64, choices=[(b'room', b'Room'), (b'talk', b'Talk')])),
                ('link_subtype', models.CharField(max_length=64, choices=[(b'beginning', b'Beginning'), (b'end', b'End')])),
                ('description', models.TextField(max_length=1024)),
            ],
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=128)),
                ('name', models.CharField(max_length=128, blank=True)),
                ('description', models.TextField(max_length=5000, blank=True)),
                ('start_time', models.DateTimeField(verbose_name=b'start time')),
                ('end_time', models.DateTimeField(verbose_name=b'end time')),
                ('state', django_fsm.FSMField(default=b'planned', max_length=50)),
                ('pub_date', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'date published', blank=True)),
                ('broadcast_id', models.CharField(default=b'', max_length=64, blank=True)),
                ('youtube_id', models.CharField(default=b'', max_length=64, blank=True)),
                ('cdn_format', models.CharField(default=b'1080p', max_length=15, choices=[(b'1080p', b'1080p'), (b'1080p_hfr', b'1080p_hfr'), (b'720p', b'720p'), (b'720_hfr', b'720p_hfr'), (b'480p', b'480p'), (b'360p', b'360p'), (b'240p', b'240p')])),
                ('stream_name', models.CharField(default=b'', max_length=45, blank=True)),
                ('ingestion_address', models.CharField(default=b'', max_length=128, blank=True)),
                ('backup_address', models.CharField(default=b'', max_length=128, blank=True)),
                ('is_streaming', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Talk',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(max_length=1024)),
                ('talk_url', models.CharField(default=b'', max_length=256, blank=True)),
                ('speaker_name', models.CharField(default=b'', max_length=128, blank=True)),
                ('speaker_url', models.CharField(default=b'', max_length=256, blank=True)),
                ('state', models.CharField(default=b'created', max_length=64, choices=[(b'revoked', b'Revoked'), (b'reclaimed', b'Reclaimed'), (b'abandoned', b'Abandoned'), (b'created', b'Created'), (b'ready', b'Ready'), (b'testStarting', b'TestStarting'), (b'testing', b'Testing'), (b'liveStarting', b'LiveStarting'), (b'live', b'Live'), (b'complete', b'Complete')])),
                ('start_time', models.DateTimeField(verbose_name=b'start time')),
                ('end_time', models.DateTimeField(verbose_name=b'end time')),
                ('pub_date', models.DateTimeField(default=datetime.datetime(2016, 1, 10, 4, 41, 35, 431144), verbose_name=b'date published', blank=True)),
                ('broadcast_id', models.CharField(default=b'', max_length=64, blank=True)),
                ('room', models.ForeignKey(to='room.Room')),
            ],
        ),
    ]
