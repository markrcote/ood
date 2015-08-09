# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ood', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='serverstate',
            name='state',
            field=models.CharField(max_length=32, null=True),
        ),
    ]
