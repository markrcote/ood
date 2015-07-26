from datetime import timedelta

UPDATE_STATE_PERIOD_SECONDS = 60

BROKER_URL = 'amqp://'
CELERY_IMPORTS = ('ood.tasks',)
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TIMEZONE = 'America/Montreal'

CELERYBEAT_SCHEDULE = {
    'update-state': {
        'task': 'ood.tasks.update_state',
        # TODO: The schedule should be frequent, but
        # DropletController.update_state() should be smarter about
        # timeouts.
        'schedule': timedelta(seconds=UPDATE_STATE_PERIOD_SECONDS),
    },
}
