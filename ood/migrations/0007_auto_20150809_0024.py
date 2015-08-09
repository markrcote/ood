# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ood', '0006_serverstate_ip_address'),
    ]

    operations = [
        migrations.RenameField(
            model_name='serverstate',
            old_name='ip_address',
            new_name='droplet_ip_address',
        ),
        migrations.AddField(
            model_name='serverstate',
            name='droplet_port',
            field=models.IntegerField(null=True),
        ),
    ]
