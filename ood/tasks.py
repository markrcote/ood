from __future__ import absolute_import

from ood.celery import app
from ood.models import OodInstance
from ood.states.simple import StateMachine


@app.task
def update_state():
    instances = OodInstance.objects.all()
    for instance in instances:
        if instance.server_type == OodInstance.SIMPLE_SERVER:
            sm = StateMachine(instance)
            sm.update()


@app.task
def start():
    # TODO: Take argument of instance id.
    instance = OodInstance.objects.get(pk=1)
    sm = StateMachine(instance)
    if not sm.controller.running():
        sm.controller.start()
        sm.go_to_state('starting')


@app.task
def stop():
    # TODO: Take argument of instance id.
    instance = OodInstance.objects.get(pk=1)
    sm = StateMachine(instance)
    if sm.controller.running():
        sm.controller.stop()
        sm.go_to_state('stopping')
