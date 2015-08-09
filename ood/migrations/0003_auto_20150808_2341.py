# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ood', '0002_auto_20150808_1651'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='serverstate',
            options={'permissions': (('start', 'Can start up server'),)},
        ),
    ]
