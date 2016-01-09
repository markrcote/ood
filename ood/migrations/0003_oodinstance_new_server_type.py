# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ood', '0002_auto_20160109_1229'),
    ]

    operations = [
        migrations.AddField(
            model_name='oodinstance',
            name='new_server_type',
            field=models.CharField(default=b'SS', max_length=2, choices=[(b'SS', b'simple server'), (b'DO', b'DigitalOcean droplet')]),
        ),
    ]
