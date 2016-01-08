# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('room', '0001_initial'),
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
        migrations.RenameField(
            model_name='room',
            old_name='ytid',
            new_name='youtube_id',
        ),
        migrations.AddField(
            model_name='room',
            name='broadcast_id',
            field=models.CharField(default=b'', max_length=64, blank=True),
        ),
        migrations.AlterField(
            model_name='room',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2016, 1, 8, 0, 55, 16, 420564), verbose_name=b'date published', blank=True),
        ),
        migrations.AlterField(
            model_name='room',
            name='state',
            field=django_fsm.FSMField(default=b'planned', max_length=50),
        ),
        migrations.AlterField(
            model_name='room',
            name='stream_name',
            field=models.CharField(default=b'', max_length=45, blank=True),
        ),
        migrations.AlterField(
            model_name='talk',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2016, 1, 8, 0, 55, 16, 422276), verbose_name=b'date published', blank=True),
        ),
    ]
