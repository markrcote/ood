from __future__ import absolute_import

from ood.celery import app
from ood.droplet import DropletController


@app.task
def update_state():
    dc = DropletController()
    dc.update_state()


@app.task
def start():
    dc = DropletController()
    dc.start()


@app.task
def stop():
    dc = DropletController()
    dc.stop()
