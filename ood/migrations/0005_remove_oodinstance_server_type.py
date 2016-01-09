# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ood', '0004_oodinstance_migrate_server_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='oodinstance',
            name='server_type',
        ),
    ]
