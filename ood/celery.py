from __future__ import absolute_import

import logging
import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ood.settings')

from django.conf import settings

logging.getLogger('requests').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

app = Celery('ood')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

if __name__ == '__main__':
    app.start()
