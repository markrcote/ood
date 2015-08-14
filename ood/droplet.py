import errno
import logging
import os
import re
import socket
import time
from datetime import timedelta
from operator import attrgetter

import digitalocean
from django.utils import timezone
from paramiko.client import AutoAddPolicy, SSHClient

from ood.contrib.MCRcon.mcrcon import MCRcon
from ood.models import ServerState


DROPLET_NAME = 'ood'
# TODO: Make all this configurable.
REGION = 'nyc3'
MINECRAFT_PORT = 25898
MINECRAFT_RCON_PORT = 25899

STATE_ARCHIVED = 'archived'
STATE_RESTORING = 'restoring'
STATE_BOOTING = 'booting'
STATE_STARTING = 'starting'
STATE_RUNNING = 'running'
STATE_STOPPING = 'stopping'
STATE_SHUTTING_DOWN = 'shutting down'
STATE_SNAPSHOTTING = 'snapshotting'
STATE_DESTROYING = 'destroying'
STATE_UNKNOWN = 'unknown'

NUM_PLAYERS_RE = re.compile('There are (\d+)/\d+ players')
MAX_TIMEDELTA_NO_PLAYERS = timedelta(minutes=15)

DEFAULT_DATA_DIR = os.path.join(os.getenv('HOME'), '.ood')
DROPLET_KEY_FILENAME = 'droplet_key'
DROPLET_ROOT_SSH_KEY_FILENAME = 'ssh_key'
RCON_PW_FILENAME = 'rcon_pw'


class DropletController(object):
    """Controls a DigitalOcean droplet running Minecraft.

    Requires an existing snapshot of the form 'ood-<timestamp>'.

    TODO: Split this into at least two classes, one for interfacing with
    the DO API/server/game, and one for the state machine.  There is way too
    much smushed together here.

    TODO: Timeouts aren't handled very well in a few places; they have a
    tendency to drift.  Not a huge deal, but ugly.

    TODO: Locks around actions.

    TODO: Analyze consistency.  Instantiations of this class are meant to be
    short lived, so grabbing all external data upon creation is more
    consistent, if potentially out of date (we do not do this right now, but
    probably should).  However inconsistencies are still possible; need to
    map all combinations.
    """

    def __init__(self, data_dir=DEFAULT_DATA_DIR):
        self.data_dir = os.path.expanduser(data_dir)
        if not os.path.exists(self.data_dir):
            os.mkdir(self.data_dir)

        self.api_key_path = os.path.join(self.data_dir, DROPLET_KEY_FILENAME)
        self.ssh_key_path = os.path.join(self.data_dir,
                                         DROPLET_ROOT_SSH_KEY_FILENAME)
        self.rcon_pw_path = os.path.join(self.data_dir, RCON_PW_FILENAME)

        self._snapshot_action = None

        self._refresh_state()
        self._refresh_droplet()

        if self.ss.state is None:
            logging.info('No saved state; trying to guess.')

            self._set_state(STATE_ARCHIVED)
            if self.droplet:
                if self.droplet.status == 'off':
                    logging.error('Droplet found but off; not sure what the '
                                  'current state is.')
                    self._set_state(STATE_UNKNOWN)
                self.update_state()
            else:
                logging.info('Droplet is not running.')
        else:
            logging.info('Starting up in state %s.' % self.ss.state)
            if self.ss.state == STATE_RUNNING:
                logging.info('Minecraft is running on %s:%d' %
                             (self.droplet_ip, MINECRAFT_PORT))
                logging.info('Player last seen %s ago.' %
                             (timezone.now() - self.ss.last_time_seen_player,))

    def start(self):
        """Starts up a droplet from the most recent snapshot."""
        if self.ss.state != STATE_ARCHIVED:
            logging.error('Cannot start Minecraft in state %s.' %
                          self.ss.state)
            return

        snapshot = self._find_snapshot()
        if snapshot is None:
            logging.error('No ood snapshot found.')
            return

        ssh_key = self._find_ssh_key()
        if ssh_key is None:
            logging.error('No ood ssk key found.')
            return

        self.droplet = digitalocean.Droplet(token=self.api_key,
                                            name='ood',
                                            region=REGION,
                                            image=snapshot.id,
                                            size_slug='1gb',
                                            ssh_keys=[ssh_key])
        self.droplet.create()

        # TODO: We need to set to an intermediate state, say,
        # 'starting', so that the UI knows we have started executing the
        # given command.

    def stop(self):
        """Starts the stop-snapshot-destroy process."""
        if self.ss.state != STATE_RUNNING:
            logging.error('Cannot stop Minecraft in state %s.' % self.ss.state)
            return

        self._refresh_droplet()
        logging.info('Stopping Minecraft.')
        self._exec_ssh_cmd('supervisorctl stop minecraft')
        self._set_state(STATE_STOPPING)

    def update_state(self):
        # TODO: The state transitions really should be encapsulated better.
        # It should be more obvious to what states and how a state can
        # transition.  The following rules are hard to understand and hence
        # fragile.  See mozpool for inspiration.
        #
        # TODO: States should have their own timeouts.
        self._refresh_droplet()

        if self.ss.state == STATE_UNKNOWN:
            return

        # Some conditions cause direct movement to a particular state.

        if self.droplet is None or self.droplet.status == 'archive':
            self._set_state(STATE_ARCHIVED)
            return

        if self.droplet.status == 'new':
            self._set_state(STATE_RESTORING)

        # Most state transitions depend on the current state and some
        # other condition(s).

        if self.droplet.status == 'off':
            # State should either be SHUTTING_DOWN or SNAPSHOTTING or
            # DESTROYING.
            if self.ss.state not in (STATE_SNAPSHOTTING, STATE_DESTROYING):
                shutdown_error = False

                if self.ss.state != STATE_SHUTTING_DOWN:
                    logging.warning('Droplet status changed to shutting down '
                                    'while in state %s.' % self.ss.state)
                    shutdown_error = True

                self._snapshot(shutdown_error)
                self._set_state(STATE_SNAPSHOTTING)

        if self.ss.state == STATE_ARCHIVED or self.ss.state == STATE_RESTORING:
            if self.droplet.status == 'active':
                self._set_state(STATE_STARTING)

        if self.ss.state == STATE_STARTING:
            if self._minecraft_port_open():
                self._set_state(STATE_RUNNING)
                # We haven't seen a player yet, but we need to given them
                # time to join.
                self.ss.last_time_seen_player = timezone.now()
                self.ss.droplet_ip_address = self.droplet_ip
                self.ss.droplet_port = MINECRAFT_PORT
                self.ss.save()
                logging.info('Minecraft available on %s:%d.' %
                             (self.droplet_ip, MINECRAFT_PORT))

        if self.ss.state == STATE_RUNNING:
            self._check_players()
            if (timezone.now() > (self.ss.last_time_seen_player +
                                  MAX_TIMEDELTA_NO_PLAYERS)):
                logging.info('No players for the last %s.' %
                             (timezone.now() - self.ss.last_time_seen_player))
                self.stop()
            # TODO: maybe move to STOPPING after a certain number of socket
            # errors.

        if self.ss.state == STATE_STOPPING:
            if not self._minecraft_port_open():
                self._shutdown()

        if self.ss.state == STATE_SNAPSHOTTING:
            if self.snapshot_action is None:
                logging.error('No snapshot action while in SNAPSHOTTING '
                              'state!')
                self._set_state(STATE_UNKNOWN)
                # TODO: we could try to find an in-progress snapshot action
                # associated with our droplet, if we have one.
                return

            if self.snapshot_action.status == 'completed':
                logging.info('Snapshot completed: %s %s.' %
                             (self.snapshot_action.resource_type,
                              self.snapshot_action.resource_id))
                self.ss.snapshot_action_id = None
                self.ss.save()
                self.droplet.destroy()
                self._set_state(STATE_DESTROYING)
            elif self.snapshot_action.status == 'errored':
                logging.error('Error taking snapshot!')
                self._set_state(STATE_UNKNOWN)

        # DESTROYING should progress to ARCHIVED through a general state
        # change above.

    @property
    def api_key(self):
        return file(self.api_key_path).read().strip()

    @property
    def droplet_ip(self):
        # TODO: Should maybe refresh droplet here.  Dependencies are unclear.
        if self.droplet is None:
            return None

        for network in self.droplet.networks['v4']:
            if network['type'] == 'public':
                return network['ip_address']

        return None

    @property
    def manager(self):
        return digitalocean.Manager(token=self.api_key)

    @property
    def snapshot_action(self):
        if self.ss.snapshot_action_id is None:
            return None
        if (self._snapshot_action is None or
            self._snapshot_action.id != self.ss.snapshot_action_id):
            # TODO: The action might not exist anymore, in which case we need
            # to clear the id variable.
            self._snapshot_action = digitalocean.Action.get_object(
                self.api_key, self.ss.snapshot_action_id)
        return self._snapshot_action

    def _find_ssh_key(self):
        for key in self.manager.get_all_sshkeys():
            if key.name == 'ood':
                return key
        return None

    def _find_snapshot(self):
        snapshots = sorted([img for img in self.manager.get_my_images()
                            if img.name.startswith('%s-' % DROPLET_NAME)],
                           key=attrgetter('name'), reverse=True)

        if not snapshots:
            return None

        return snapshots[0]

    def _refresh_droplet(self):
        for droplet in self.manager.get_all_droplets():
            if droplet.name == DROPLET_NAME:
                self.droplet = droplet
                break
        else:
            self.droplet = None

    def _set_state(self, new_state):
        if self.ss.state is None:
            logging.info('Setting initial state to %s.' % (new_state))
        elif self.ss.state == new_state:
            return
        else:
            logging.info('State changed from %s to %s.' % (self.ss.state,
                                                           new_state))

        self.ss.state = new_state
        self.ss.save()

    def _minecraft_port_open(self):
        if self.droplet_ip is None:
            return False

        try:
            s = socket.create_connection((self.droplet_ip, MINECRAFT_PORT),
                                         timeout=5)
        except socket.error as e:
            if e.errno != errno.ECONNREFUSED:
                logging.warning('Unexpected socket error when checking '
                                'Minecraft port: %s' % e)
            return False
        except socket.timeout:
            return False

        s.close()
        return True

    def _snapshot(self, shutdown_error):
        if self.droplet is None:
            logging.error('Cannot start snapshot: no droplet.')
            return

        if self.snapshot_action:
            logging.error('Cannot start snapshot: snapshot in progress.')
            return

        snapshot_name = '%s-%d' % (DROPLET_NAME, time.time())
        if shutdown_error:
            snapshot_name += '-error'

        self.ss.snapshot_action_id = self.droplet.take_snapshot(snapshot_name)[
            'action']['id']
        self.ss.save()

    def _exec_ssh_cmd(self, cmdline):
        client = SSHClient()
        client.set_missing_host_key_policy(AutoAddPolicy())
        client.connect(self.droplet_ip, username='root',
                       key_filename=self.ssh_key_path)
        stdin, stdout, stderr = client.exec_command(cmdline)
        for line in stdout:
            logging.info(line)
        for line in stderr:
            logging.info(line)

    def _shutdown(self):
        logging.info('Shutting down host.')
        self.droplet.shutdown()
        self._set_state(STATE_SHUTTING_DOWN)
        # TODO: Keep the action object and use it to verify state (but
        # double check that the state is 'off' after).
        # TODO: Call self.droplet.poweroff() if shutdown() fails or takes
        # too long.

    def _num_players(self):
        rcon = MCRcon()
        try:
            rcon.connect(self.droplet_ip, MINECRAFT_RCON_PORT)
            rcon.login(file(self.rcon_pw_path).read().strip())
            out = rcon.command('/list')
        except socket.error as e:
            # TODO: We should log errors if we get connection-refused
            # errors for too long.
            if e.errno != errno.ECONNREFUSED:
                logging.warning('Unexpected socket error when accessing '
                                'Minecraft RCON port: %s' % e)
            return 0

        m = NUM_PLAYERS_RE.match(out)

        if not m:
            logging.error('Invalid output from /list: %s' % out)
            return

        return int(m.group(1))

    def _check_players(self):
        if self.ss.last_time_seen_player is None or self._num_players() > 0:
            self.ss.last_time_seen_player = timezone.now()
            self.ss.save()

    def _refresh_state(self):
        # TODO: This assumes there is only one entry in the table (i.e. one
        # server).
        self.ss = ServerState.objects.get(id=1)
