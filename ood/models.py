from django.db import models


class OodInstance(models.Model):
    SIMPLE_SERVER = 0
    DROPLET_SERVER = 1

    class Meta:
        permissions = (
            ('can_start', 'Can start up server'),
            ('can_stop', 'Can stop the server'),
        )

    name = models.CharField(max_length=64)
    server_type = models.SmallIntegerField()
    state = models.CharField(max_length=32, null=True)
    last_state_update = models.DateTimeField(null=True)


class MineCraftServerSettings(models.Model):
    ood = models.ForeignKey(OodInstance)
    ip_address = models.GenericIPAddressField(null=True)
    port = models.IntegerField()
    rcon_port = models.IntegerField()
    rcon_password = models.CharField(max_length=64)


class ServerPlayerState(models.Model):
    ood = models.ForeignKey(OodInstance)
    last_time_seen_player = models.DateTimeField(null=True)
    last_time_checked_players = models.DateTimeField(null=True)
    num_players = models.IntegerField(null=True)


class DropletState(models.Model):
    """Captures the state for one server.

    TODO: This is a mix of general and specific stuff and should probably be
    separated out at some point.  Some is specific to particular states
    and some to particular cloud hosts.
    """
    ood = models.ForeignKey(OodInstance)
    snapshot_action_id = models.IntegerField(null=True)
    droplet_ip_address = models.GenericIPAddressField(null=True)
    droplet_port = models.IntegerField(null=True)


class SimpleServerState(models.Model):
    ood = models.ForeignKey(OodInstance)
    ip_address = models.GenericIPAddressField(null=True)
    port = models.IntegerField(null=True)
