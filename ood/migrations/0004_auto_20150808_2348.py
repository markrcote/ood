# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ood', '0003_auto_20150808_2341'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='serverstate',
            options={'permissions': (('can_start', 'Can start up server'),)},
        ),
    ]
