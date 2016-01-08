# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('room', '0002_auto_20160108_0055'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='room',
            name='title',
        ),
        migrations.AddField(
            model_name='room',
            name='is_streaming',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='room',
            name='description',
            field=models.TextField(max_length=5000, blank=True),
        ),
        migrations.AlterField(
            model_name='room',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2016, 1, 8, 2, 47, 56, 925066), verbose_name=b'date published', blank=True),
        ),
        migrations.AlterField(
            model_name='talk',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2016, 1, 8, 2, 47, 56, 926967), verbose_name=b'date published', blank=True),
        ),
    ]
