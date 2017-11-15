#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

'''
Created by zhaopan on 2017/10/30.
'''

__author__ = 'zhaopan'

from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.views.generic.base import TemplateView

common_form_template = 'registration/template_form.html'
from accounts.forms import ExRegistrationView, ExAuthenticationForm, ExPasswordChangeForm, common_form_template




urlpatterns = [
    url(r'^register/$',
        # views.RegistrationView.as_view(),
        ExRegistrationView.as_view(),
        name='registration_register'),
    url(r'^register/closed/$',
        TemplateView.as_view(
            template_name='registration/registration_closed.html'
        ),
        name='registration_disallowed'),

    url(r'^login/$',
        auth_views.login,
        {'template_name': 'registration/login.html', 'authentication_form': ExAuthenticationForm},
        name='auth_login'),
    url(r'^logout/$',
        auth_views.logout,
        {'template_name': 'registration/logout.html'},
        name='auth_logout'),
    url(r'^password/change/$',
        auth_views.password_change,
        # {'post_change_redirect': 'auth_password_change_done'},
        {'post_change_redirect': 'auth_login',
         'password_change_form': ExPasswordChangeForm,
         'template_name': common_form_template},
        name='auth_password_change'),
    url(r'^password/change/done/$',
        auth_views.password_change_done,
        name='auth_password_change_done'),
    url(r'^password/reset/$',
        auth_views.password_reset,
        {'post_reset_redirect': 'auth_password_reset_done',
         'email_template_name': 'registration/password_reset_email.txt'},
        name='auth_password_reset'),
    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/'
        r'(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm,
        {'post_reset_redirect': 'auth_password_reset_complete'},
        name='auth_password_reset_confirm'),
    url(r'^password/reset/complete/$',
        auth_views.password_reset_complete,
        name='auth_password_reset_complete'),
    url(r'^password/reset/done/$',
        auth_views.password_reset_done,
        name='auth_password_reset_done'),
]
