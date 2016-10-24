from django.db import models


class OodInstance(models.Model):
    SIMPLE_SERVER = 'SS'
    DROPLET_SERVER = 'DO'
    SERVER_TYPE_CHOICES = (
        (SIMPLE_SERVER, 'simple server'),
        (DROPLET_SERVER, 'DigitalOcean droplet')
    )

    class Meta:
        permissions = (
            ('can_start', 'Can start up server'),
            ('can_stop', 'Can stop the server'),
            ('can_add', 'Can add new instances'),
            ('can_edit', 'Can edit existing instances'),
        )

    name = models.CharField(max_length=64)
    server_type = models.CharField(max_length=2,
                                   choices=SERVER_TYPE_CHOICES,
                                   default=SIMPLE_SERVER)
    state = models.CharField(max_length=32, null=True)
    last_state_update = models.DateTimeField(null=True)

    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.get_server_type_display())


class MineCraftServerSettings(models.Model):
    """Settings for a specific MineCraft server.
    Some of these might change depending on the instance type.
    TODO: These settings are updated by ood.minecraft.Client.update_host(),
    which at the moment is only called by
    ood.controllers.droplet.DropletController.  It should be clearer whether
    these settings are static or dynamic.
    """
    ood = models.OneToOneField(OodInstance)
    ip_address = models.GenericIPAddressField(null=True)
    port = models.IntegerField(null=True)
    rcon_port = models.IntegerField(null=True)
    rcon_password = models.CharField(max_length=64, null=True)


class ServerPlayerState(models.Model):
    ood = models.OneToOneField(OodInstance)
    last_time_seen_player = models.DateTimeField(null=True)
    last_time_checked_players = models.DateTimeField(null=True)
    num_players = models.IntegerField(null=True)


class DropletState(models.Model):
    """Captures the state for one server.

    TODO: This is a mix of general and specific stuff and should probably be
    separated out at some point.  Some is specific to particular states
    and some to particular cloud hosts.
    """
    ood = models.OneToOneField(OodInstance)
    name = models.CharField(max_length=32, default='ood')
    snapshot_action_id = models.IntegerField(null=True)
    droplet_ip_address = models.GenericIPAddressField(null=True)
    region = models.CharField(max_length=64, default='nyc3')
    # Needs to be an RSA key at the moment.
    pkey = models.TextField(null=True)


class SimpleServerState(models.Model):
    ood = models.OneToOneField(OodInstance)
    ip_address = models.GenericIPAddressField(null=True)
    port = models.IntegerField(null=True)
