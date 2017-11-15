# -*- coding: utf-8 -*-

from django.conf.urls import url
from .views import IndexView, VerifyView, detail
from django.contrib.auth.decorators import login_required

urlpatterns = [
  url(r'^$', login_required(IndexView.as_view()), name='page'),
  url(r'^verify$', VerifyView.as_view(), name='verify-page'),
  url(r'^(?P<page_id>[0-9A-Za-z-]+)$', login_required(detail), name='page-detail'),
]
