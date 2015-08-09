# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ood', '0005_auto_20150808_2358'),
    ]

    operations = [
        migrations.AddField(
            model_name='serverstate',
            name='ip_address',
            field=models.GenericIPAddressField(null=True),
        ),
    ]
