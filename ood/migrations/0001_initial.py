# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DropletState',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('snapshot_action_id', models.IntegerField(null=True)),
                ('droplet_ip_address', models.GenericIPAddressField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='MineCraftServerSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ip_address', models.GenericIPAddressField(null=True)),
                ('port', models.IntegerField(null=True)),
                ('rcon_port', models.IntegerField(null=True)),
                ('rcon_password', models.CharField(max_length=64, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='OodInstance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64)),
                ('server_type', models.SmallIntegerField()),
                ('state', models.CharField(max_length=32, null=True)),
                ('last_state_update', models.DateTimeField(null=True)),
            ],
            options={
                'permissions': (('can_start', 'Can start up server'), ('can_stop', 'Can stop the server')),
            },
        ),
        migrations.CreateModel(
            name='ServerPlayerState',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_time_seen_player', models.DateTimeField(null=True)),
                ('last_time_checked_players', models.DateTimeField(null=True)),
                ('num_players', models.IntegerField(null=True)),
                ('ood', models.OneToOneField(to='ood.OodInstance')),
            ],
        ),
        migrations.CreateModel(
            name='SimpleServerState',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ip_address', models.GenericIPAddressField(null=True)),
                ('port', models.IntegerField(null=True)),
                ('ood', models.OneToOneField(to='ood.OodInstance')),
            ],
        ),
        migrations.AddField(
            model_name='minecraftserversettings',
            name='ood',
            field=models.OneToOneField(to='ood.OodInstance'),
        ),
        migrations.AddField(
            model_name='dropletstate',
            name='ood',
            field=models.OneToOneField(to='ood.OodInstance'),
        ),
    ]
