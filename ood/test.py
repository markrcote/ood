# Some convenience settings and functions for testing.

import logging

log_format = '%(asctime)s:%(levelname)s:%(name)s:%(message)s'
logging.basicConfig(format=log_format, level=logging.INFO,
                    datefmt='%Y-%m-%d %H:%M:%S')
logging.getLogger("requests").setLevel(logging.WARNING)

from ood.droplet import DropletController


def new():
    return DropletController('~/.ood/droplet_key', '~/.ood/ssh_key',
                             '~/.ood/rcon_pw')
