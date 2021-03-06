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
        migrations.AddField(
            model_name='room',
            name='hostname',
            field=models.CharField(default=b'', max_length=128, blank=True),
        ),
        migrations.AddField(
            model_name='room',
            name='mac_address',
            field=models.CharField(default=b'', max_length=64, blank=True),
        ),
        migrations.AlterField(
            model_name='talk',
            name='state',
            field=django_fsm.FSMField(default=b'created', max_length=50),
        ),
    ]
