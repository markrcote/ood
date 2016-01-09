# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ood', '0005_remove_oodinstance_server_type'),
    ]

    operations = [
        migrations.RenameField(
            model_name='oodinstance',
            old_name='new_server_type',
            new_name='server_type',
        ),
    ]
