# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ood', '0006_auto_20160109_1432'),
    ]

    operations = [
        migrations.AddField(
            model_name='dropletstate',
            name='pkey',
            field=models.TextField(null=True),
        ),
    ]
