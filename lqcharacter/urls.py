# -*- coding: utf-8 -*-
"""lqcharacter URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
import xadmin

# xadmin.autodiscover()

# version模块自动注册需要版本控制的 Model
from xadmin.plugins import xversion
xversion.register_models()

urlpatterns = [
    url(r'^', include("core.dashboard.urls"), name='dashboard'),
    url(r'^xadmin/', xadmin.site.urls),
    url(r'^pages/', include("core.page.urls"), name='pages'),
    url(r'^rects/', include("core.rect.urls"), name='rects'),
    url(r'^api/', include("api.urls")),
    #url(r'^accounts/', include('registration.backends.simple.urls')),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^files/', include('db_file_storage.urls')),
]
