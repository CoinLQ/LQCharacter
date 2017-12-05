# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.contrib.contenttypes.models import ContentType

@shared_task
def clean_daily_page():
    page_klass = ContentType.objects.get(app_label='core', model='page').model_class()
    page_klass.objects.filter(locked=1).update(locked=0)
