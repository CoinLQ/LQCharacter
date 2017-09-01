# coding=utf-8

from django.conf.urls import url
from .views import IndexView, detail


urlpatterns = [
  url(r'^(?P<page_id>[0-9A-Za-z-]+)$', detail, name='page-detail'),
  url(r'^$', IndexView.as_view(), name='page'),
]