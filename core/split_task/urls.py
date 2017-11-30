# -*- coding: utf-8 -*-

from django.conf.urls import url
from .views import SplitListView, detail
from django.contrib.auth.decorators import login_required

urlpatterns = [
  url(r'^$', login_required(SplitListView.as_view()), name='split-list'),
  url(r'^(?P<rect_id>[0-9A-Za-z-]+)$', detail, name='split-detail'),
]
