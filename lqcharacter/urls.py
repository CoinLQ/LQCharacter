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
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views.static import serve #处理静态文件
from rest_framework import routers
import xadmin
# xadmin.autodiscover()

# version模块自动注册需要版本控制的 Model
from xadmin.plugins import xversion
xversion.register_models()

urlpatterns = [
    url(r'^', include("core.dashboard.urls"), name='dashboard'),
    url(r'^xadmin/', xadmin.site.urls, name=xadmin),
    url(r'^pages/', include("core.page.urls"), name='pages'),
    url(r'^rects/', include("core.rect.urls"), name='rects'),
    url(r'^api/', include("api.urls")),
    #url(r'^accounts/', include('registration.backends.simple.urls')),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^files/', include('db_file_storage.urls')),
]

# 全局 404 处理函数
def page_not_found(request):
    from django.shortcuts import render_to_response
    response = render_to_response('404.html', {})
    response.status_code = 404
    return response

# 全局 500 处理函数
def page_error(request):
    from django.shortcuts import render_to_response
    response = render_to_response('500.html', {})
    response.status_code = 500
    return response

# 全局 404 页面配置（django 会自动调用这个变量）
handler404 = 'setting.urls.page_not_found'
handler500 = 'setting.urls.page_error'

if settings.DEBUG:
    # debug_toolbar 插件配置
    import debug_toolbar
    urlpatterns.append(url(r'^__debug__/', include(debug_toolbar.urls)))
else:
    # 项目部署上线时使用
    from lqcharacter.settings import STATIC_ROOT
    # 配置静态文件访问处理
    urlpatterns.append(url(r'^static/(?P<path>.*)$', serve, {'document_root': STATIC_ROOT}))