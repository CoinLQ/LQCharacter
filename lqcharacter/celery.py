from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lqcharacter.settings')

app = Celery('lqcharacter', broker='redis://localhost:6379/0')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
# USE_TZ = True
# TIME_ZONE = 'Europe/Moscow'

CELERY_ENABLE_UTC = True

app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.update(
    task_serializer='json',
    accept_content=['application/json'],  # Ignore other content
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=False,
)

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls test('every_minute') every 60 seconds.
    sender.add_periodic_task(60.0, every_minute.s(), name='add every minute')

    # Executes every day at 1:02 a.m.
    sender.add_periodic_task(
        crontab(hour='1', minute='02', day_of_week="*"),
        every_morning.s(), name='good morning')

    # Calls test('world') every 30 seconds
    # sender.add_periodic_task(10.0, test.s(''), expires=10)




@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

@app.task
def every_morning():
    from core.tasks import clean_daily_page
    clean_daily_page()
    return 'good morning'

@app.task
def every_minute():
    return 'every_minute'

@app.task
def test(arg):
    print(arg)