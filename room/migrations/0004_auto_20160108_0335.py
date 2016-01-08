# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('room', '0003_auto_20160108_0247'),
    ]

    operations = [
        migrations.AddField(
            model_name='talk',
            name='broadcast_id',
            field=models.CharField(default=b'', max_length=64, blank=True),
        ),
        migrations.AlterField(
            model_name='room',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2016, 1, 8, 3, 35, 12, 350742), verbose_name=b'date published', blank=True),
        ),
        migrations.AlterField(
            model_name='talk',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2016, 1, 8, 3, 35, 12, 352765), verbose_name=b'date published', blank=True),
        ),
    ]
