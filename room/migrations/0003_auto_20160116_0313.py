# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('room', '0002_auto_20160110_1704'),
    ]

    operations = [
        migrations.AlterField(
            model_name='talk',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(
                2016, 1, 16, 3, 13, 45, 184914), verbose_name=b'date published', blank=True),
        ),
    ]
