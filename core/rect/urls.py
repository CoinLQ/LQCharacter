# -*- coding: utf-8 -*-

from django.conf.urls import url
from .views import ConfidenceView, detail
from django.contrib.auth.decorators import login_required

urlpatterns = [
  url(r'^$', login_required(ConfidenceView.as_view()), name='rect-confidence'),
  url(r'^(?P<rect_id>[0-9A-Za-z-]+)$', detail, name='rect-detail'),
]
