from __future__ import absolute_import

from celery import Celery


app = Celery('ood')
app.config_from_object('ood.celeryconfig')

if __name__ == '__main__':
    app.start()
