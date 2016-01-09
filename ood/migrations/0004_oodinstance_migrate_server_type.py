# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def migrate_server_type(apps, schema_editor):
    OodInstance = apps.get_model('ood', 'OodInstance')
    for instance in OodInstance.objects.all():
        if instance.server_type == 0:
            instance.new_server_type = 'SS'
        else:
            instance.new_server_type = 'DO'
        instance.save()


class Migration(migrations.Migration):

    dependencies = [
        ('ood', '0003_oodinstance_new_server_type'),
    ]

    operations = [
        migrations.RunPython(migrate_server_type),
    ]
