# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ood', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='dropletstate',
            name='name',
            field=models.CharField(default=b'ood', max_length=32),
        ),
        migrations.AddField(
            model_name='dropletstate',
            name='region',
            field=models.CharField(default=b'nyc3', max_length=64),
        ),
    ]
