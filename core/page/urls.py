# -*- coding: utf-8 -*-

from django.conf.urls import url
from .views import IndexView, VerifyView, detail


urlpatterns = [
  url(r'^$', IndexView.as_view(), name='page'),
  url(r'^verify$', VerifyView.as_view(), name='verify-page'),
  url(r'^(?P<page_id>[0-9A-Za-z-]+)$', detail, name='page-detail'),
]
