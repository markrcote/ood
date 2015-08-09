from django.db import models


class Server(models.Model):
    name = models.CharField(max_length=64)


class ServerState(models.Model):
    """Captures the state for one server.

    TODO: This is a mix of general and specific stuff and should probably be
    separated out at some point.  Some is specific to particular states
    and some to particular cloud hosts.
    """
    class Meta:
        permissions = (
            ('can_start', 'Can start up server'),
            ('can_stop', 'Can stop the server'),
        )

    server = models.ForeignKey(Server)
    state = models.CharField(max_length=32, null=True)
    last_time_seen_player = models.DateTimeField(null=True)
    snapshot_action_id = models.IntegerField(null=True)
    droplet_ip_address = models.GenericIPAddressField(null=True)
    droplet_port = models.IntegerField(null=True)
