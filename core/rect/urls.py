# -*- coding: utf-8 -*-

from django.conf.urls import url
from .views import ConfidenceView, detail


urlpatterns = [
  url(r'^$', ConfidenceView.as_view(), name='rect-confidence'),
  url(r'^(?P<rect_id>[0-9A-Za-z-]+)$', detail, name='rect-detail'),
]
