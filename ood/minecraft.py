import errno
import logging
import re
import socket
from datetime import timedelta

from django.utils import timezone

from ood.contrib.MCRcon.mcrcon import MCRcon
from ood.models import MineCraftServerSettings, ServerPlayerState
from ood.settings import MAX_MINUTES_NO_PLAYERS

NUM_PLAYERS_RE = re.compile('There are (\d+)/\d+ players')
MAX_TIMEDELTA_NO_PLAYERS = timedelta(minutes=MAX_MINUTES_NO_PLAYERS)


class Client(object):

    def __init__(self, ood_instance):
        self.ood_instance = ood_instance
        self.settings = MineCraftServerSettings.objects.get(ood=ood_instance)
        state = self._get_state()
        if state.last_time_checked_players is None:
            state.last_time_checked_players = timezone.now()
        if state.last_time_seen_player is None:
            state.last_time_seen_player = state.last_time_checked_players
        if state.num_players is None:
            state.num_players = 0
        state.save()

    def port_open(self):
        try:
            s = socket.create_connection((self.settings.ip_address,
                                          self.settings.port),
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

    def reset_player_info(self):
        state = self._get_state()
        state.last_time_checked_players = timezone.now()
        state.last_time_seen_player = state.last_time_checked_players
        state.num_players = 0
        state.save()

    def check_for_players(self):
        state = self._get_state()
        state.last_time_checked_players = timezone.now()
        state.save()
        rcon = MCRcon()

        try:
            rcon.connect(self.settings.ip_address, self.settings.rcon_port)
            rcon.login(self.settings.rcon_password)
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
            return 0

        state.num_players = int(m.group(1))
        if state.num_players:
            state.last_time_seen_player = state.last_time_checked_players
        state.save()

    def timeout_no_players(self):
        state = self._get_state()
        return (timezone.now() > (state.last_time_seen_player +
                                  MAX_TIMEDELTA_NO_PLAYERS))

    def _get_state(self):
        state = ServerPlayerState.objects.get(ood=self.ood_instance)
        if state is None:
            state = ServerPlayerState(ood=self.ood_instance)
            state.save()
        return state
