# -*- coding: utf-8 -*-

from django.conf.urls import url
<<<<<<< HEAD
from .views import IndexView, detail


urlpatterns = [
  url(r'^(?P<page_id>[0-9A-Za-z-]+)$', detail, name='page-detail'),
  url(r'^$', IndexView.as_view(), name='page'),
=======
from .views import IndexView, VerifyView, detail


urlpatterns = [
  url(r'^$', IndexView.as_view(), name='page'),
  url(r'^verify$', VerifyView.as_view(), name='verify-page'),
  url(r'^(?P<page_id>[0-9A-Za-z-]+)$', detail, name='page-detail'),
>>>>>>> 99c8ed6aee11ee22ac644976c17712cf4c0771f5
]
