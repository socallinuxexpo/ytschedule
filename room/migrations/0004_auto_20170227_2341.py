# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('room', '0003_auto_20160116_0313'),
    ]

    operations = [
        migrations.AlterField(
            model_name='talk',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 2, 27, 23, 41, 26, 905469), verbose_name=b'date published', blank=True),
        ),
    ]
