# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(max_length=1024)),
                ('start_time', models.DateTimeField(verbose_name=b'start time')),
                ('end_time', models.DateTimeField(verbose_name=b'end time')),
                ('state', models.CharField(default=b'planned', max_length=64, choices=[(b'error', b'Error'), (b'planned', b'Planned'), (b'created', b'Created'), (b'ready', b'Ready'), (b'inactive', b'Inactive'), (b'active', b'Active')])),
                ('pub_date', models.DateTimeField(default=datetime.datetime(2015, 8, 18, 0, 52, 16, 444848), verbose_name=b'date published', blank=True)),
                ('ytid', models.CharField(default=b'', max_length=64, blank=True)),
                ('cdn_format', models.CharField(default=b'1080p', max_length=15, choices=[(b'1080p', b'1080p'), (b'1080p_hfr', b'1080p_hfr'), (b'720p', b'720p'), (b'720_hfr', b'720p_hfr'), (b'480p', b'480p'), (b'360p', b'360p'), (b'240p', b'240p')])),
                ('stream_name', models.CharField(default=b'', max_length=15, blank=True)),
                ('ingestion_address', models.CharField(default=b'', max_length=128, blank=True)),
                ('backup_address', models.CharField(default=b'', max_length=128, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Talk',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(max_length=1024)),
                ('talk_url', models.CharField(default=b'', max_length=256, blank=True)),
                ('speaker_name', models.CharField(default=b'', max_length=64, blank=True)),
                ('speaker_url', models.CharField(default=b'', max_length=256, blank=True)),
                ('state', models.CharField(default=b'created', max_length=64, choices=[(b'revoked', b'Revoked'), (b'reclaimed', b'Reclaimed'), (b'abandoned', b'Abandoned'), (b'created', b'Created'), (b'ready', b'Ready'), (b'testStarting', b'TestStarting'), (b'testing', b'Testing'), (b'liveStarting', b'LiveStarting'), (b'live', b'Live'), (b'complete', b'Complete')])),
                ('start_time', models.DateTimeField(verbose_name=b'start time')),
                ('end_time', models.DateTimeField(verbose_name=b'end time')),
                ('pub_date', models.DateTimeField(default=datetime.datetime(2015, 8, 18, 0, 52, 16, 446007), verbose_name=b'date published', blank=True)),
                ('room', models.ForeignKey(to='room.Room')),
            ],
        ),
    ]
