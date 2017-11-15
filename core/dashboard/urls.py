# coding=utf-8

from django.conf.urls import url
from .views import IndexView
from django.contrib.auth.decorators import login_required

urlpatterns = [
  url(r'^$', login_required(IndexView.as_view()), name='dashboard'),
]
