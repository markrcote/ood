from django.test import TestCase
from mock import MagicMock

from ood.models import OodInstance
from ood.states import droplet


class TestController(object):
    class TestDroplet(object):
        status = 'unknown'

    class TestClient(object):
        def __init__(self):
            self.reset_player_info = MagicMock()
            self.check_for_players = MagicMock()
            self.timeout_no_players = MagicMock(return_value=False)

    class TestSnapshotAction(object):
        def __init__(self):
            self.status = 'unknown'
            self.resource_type = 'unknown'
            self.resource_id = 0

    def __init__(self, ood_instance):
        self.ood_instance = ood_instance
        self.snapshot_action = None
        self.droplet = self.TestDroplet()
        self.mcc = self.TestClient()

        self.clear_snapshot_action = MagicMock()
        self.destroy = MagicMock()
        self.prune_snapshots = MagicMock()
        self.running = MagicMock(return_value=False)
        self.shutdown = MagicMock()
        self.snapshot = MagicMock()
        self.stop = MagicMock()


droplet.StateMachine.controller_class = TestController


class TestDropletStates(TestCase):
    """Unit tests for Droplet states.

    One slight inaccuracy here is that we are not recreating StateMachine
    objects before each timeout, which is how this works in production.
    """

    def setUp(self):
        self.ood_instance = OodInstance()
        self.ood_instance.save()
        self.sm = droplet.StateMachine(self.ood_instance)

    def test_init(self):
        # A new state machine should start in the Unknown state.
        self.assertIsInstance(self.sm.current_state(), droplet.Unknown)

    def test_archive(self):
        self.sm.go_to_state(droplet.Archived.name)

        # Archived should stay Archived after timeouts.
        self.sm.current_state().on_timeout()
        self.assertIsInstance(self.sm.current_state(), droplet.Archived)

    def test_restoring(self):
        self.sm.go_to_state(droplet.Restoring.name)

        # Restoring should stay Restoring until the droplet status becomes
        # 'active', when it will switch to Starting.
        self.sm.controller.droplet.status = 'new'
        self.sm.current_state().on_timeout()
        self.assertIsInstance(self.sm.current_state(), droplet.Restoring)

        self.sm.controller.droplet.status = 'active'
        self.sm.current_state().on_timeout()
        self.assertIsInstance(self.sm.current_state(), droplet.Starting)

    def test_starting(self):
        self.sm.go_to_state(droplet.Starting.name)

        # Starting should stay Starting until the droplet status is 'archive'
        # or 'active'.  Player info should only be reset when the status is
        # 'active' and the controller is running, at which point it moves to
        # Running.

        # Setting the droplet state to 'archive' moves the state to Archived.
        self.sm.controller.droplet.status = 'archive'
        self.sm.current_state().on_timeout()
        self.sm.controller.mcc.reset_player_info.assert_not_called()
        self.assertIsInstance(self.sm.current_state(), droplet.Archived)

        self.sm.go_to_state(droplet.Starting.name)

        self.sm.controller.droplet.status = 'active'
        self.sm.current_state().on_timeout()
        self.sm.controller.mcc.reset_player_info.assert_not_called()
        self.assertIsInstance(self.sm.current_state(), droplet.Starting)

        self.sm.controller.running.return_value = True
        self.sm.current_state().on_timeout()
        self.sm.controller.mcc.reset_player_info.assert_called()
        self.assertIsInstance(self.sm.current_state(), droplet.Running)

    def test_running(self):
        self.sm.go_to_state(droplet.Running.name)

        # Running should stay Running until the no-players timeout, in which
        # case it should go to Stopping.
        self.sm.current_state().on_timeout()
        self.assertIsInstance(self.sm.current_state(), droplet.Running)

        self.sm.controller.mcc.timeout_no_players.return_value = True
        self.sm.current_state().on_timeout()
        self.sm.controller.stop.assert_called()
        self.assertIsInstance(self.sm.current_state(), droplet.Stopping)

    def test_stopping(self):
        self.sm.go_to_state(droplet.Stopping.name)

        # Stopping should stay Stopping until the controller is no longer
        # running, at which case it moves to Snapshotting.
        self.sm.controller.running.return_value = True
        self.sm.current_state().on_timeout()
        self.sm.controller.shutdown.assert_not_called()
        self.assertIsInstance(self.sm.current_state(), droplet.Stopping)

        self.sm.controller.running.return_value = False
        self.sm.current_state().on_timeout()
        self.sm.controller.shutdown.assert_called()
        self.assertIsInstance(self.sm.current_state(), droplet.ShuttingDown)

    def test_shuttingdown(self):
        self.sm.go_to_state(droplet.ShuttingDown.name)

        # ShuttingDown should only move to Snapshotting when the droplet
        # status goes to 'off'.
        self.sm.controller.droplet.status = 'active'
        self.sm.current_state().on_timeout()
        self.sm.controller.snapshot.assert_not_called()
        self.assertIsInstance(self.sm.current_state(), droplet.ShuttingDown)

        self.sm.controller.droplet.status = 'off'
        self.sm.current_state().on_timeout()
        self.sm.controller.snapshot.assert_called()
        self.assertIsInstance(self.sm.current_state(), droplet.Snapshotting)

    def test_snapshotting(self):
        self.sm.go_to_state(droplet.Snapshotting.name)

        # Snapshotting should go to Unknown if there is no snapshot action
        # object.
        self.sm.current_state().on_timeout()
        self.assertIsInstance(self.sm.current_state(), droplet.Unknown)

        self.sm.go_to_state(droplet.Snapshotting.name)

        # Snapshotting should go to Unknown if the snapshot action status is
        # 'errored'.
        sa = self.sm.controller.TestSnapshotAction()
        self.sm.controller.snapshot_action = sa
        sa.status = 'errored'
        self.sm.current_state().on_timeout()
        self.assertIsInstance(self.sm.current_state(), droplet.Unknown)

        self.sm.go_to_state(droplet.Snapshotting.name)

        # Snapshotting should stay as Snapshotting otherwise, until
        # the snapshot action status 'completed'.
        sa.status = 'in-progress'
        self.sm.current_state().on_timeout()
        self.assertIsInstance(self.sm.current_state(), droplet.Snapshotting)

        # None of these should have been called to this point.
        self.sm.controller.clear_snapshot_action.assert_not_called()
        self.sm.controller.destroy.assert_not_called()
        self.sm.controller.prune_snapshots.assert_not_called()

        sa.status = 'completed'
        self.sm.current_state().on_timeout()
        self.sm.controller.clear_snapshot_action.assert_called()
        self.sm.controller.destroy.assert_called()
        self.sm.controller.prune_snapshots.assert_called()
        self.assertIsInstance(self.sm.current_state(), droplet.Destroying)

    def test_destroying(self):
        self.sm.go_to_state(droplet.Destroying.name)

        # Destroying can only go to Archived, by the inherited way of the
        # seeing the droplet status turn to 'arcehive'.
        self.sm.controller.droplet.status = 'off'
        self.sm.current_state().on_timeout()
        self.assertIsInstance(self.sm.current_state(), droplet.Destroying)

        self.sm.controller.droplet.status = 'archive'
        self.sm.current_state().on_timeout()
        self.assertIsInstance(self.sm.current_state(), droplet.Archived)
