from django.test import TestCase

from ood.models import OodInstance
from ood.states import droplet


class TestController(object):
    class TestDroplet(object):
        status = 'unknown'

    class TestClient(object):
        def reset_player_info(self):
            pass

    def __init__(self, ood_instance):
        self.ood_instance = ood_instance
        self.droplet = self.TestDroplet()
        self.mcc = self.TestClient()
        self._running = False

    def running(self):
        return self._running


droplet.StateMachine.controller_class = TestController


class TestDropletStates(TestCase):

    def setUp(self):
        self.ood_instance = OodInstance()
        self.ood_instance.save()
        self.sm = droplet.StateMachine(self.ood_instance)

    def test_init(self):
        self.assertEqual(self.sm.current_state().name, 'unknown')

    def test_archive(self):
        self.assertIsInstance(self.sm.current_state(), droplet.Unknown)
        self.sm.go_to_state(droplet.Archived.name)
        self.assertIsInstance(self.sm.current_state(), droplet.Archived)

        self.sm.current_state().on_timeout()
        self.assertIsInstance(self.sm.current_state(), droplet.Archived)

    def test_restoring(self):
        self.sm.go_to_state(droplet.Restoring.name)
        self.assertIsInstance(self.sm.current_state(), droplet.Restoring)

        self.sm.current_state().on_timeout()
        self.assertIsInstance(self.sm.current_state(), droplet.Restoring)

        self.sm.controller.droplet.status = 'active'
        self.sm.current_state().on_timeout()
        self.assertIsInstance(self.sm.current_state(), droplet.Starting)

    def test_starting(self):
        self.sm.go_to_state(droplet.Starting.name)
        self.sm.current_state().on_timeout()
        self.assertIsInstance(self.sm.current_state(), droplet.Starting)

        self.sm.controller._running = True
        self.sm.controller.droplet.status = 'archive'
        self.sm.current_state().on_timeout()
        self.assertIsInstance(self.sm.current_state(), droplet.Archived)

        self.sm.go_to_state(droplet.Starting.name)
        self.sm.controller.droplet.status = 'active'
        self.sm.current_state().on_timeout()
        self.assertIsInstance(self.sm.current_state(), droplet.Running)
