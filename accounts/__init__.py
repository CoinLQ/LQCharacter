#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

'''
Created by zhaopan on 2017/10/30.
'''

__author__ = 'zhaopan'

from django.conf import settings
from accounts.mail import send_mail

CONF_EMAIL = settings.CONF_EMAIL

def send_html_mail(to, subject, content):
    send_mail(
        CONF_EMAIL['smtp_host'],
        CONF_EMAIL['smtp_port'],
        CONF_EMAIL['username'],
        CONF_EMAIL['password'],
        CONF_EMAIL['from'],
        to,
        subject,
        content,
        'html',
        CONF_EMAIL['display_from']
    )



