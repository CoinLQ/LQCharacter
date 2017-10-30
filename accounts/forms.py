#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

'''
Created by zhaopan on 2017/10/30.
'''

__author__ = 'zhaopan'

from django.template import Template
from material import Layout, Row, Column, Fieldset, Span2, Span3, Span5, Span6, Span10
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from registration.forms import RegistrationForm
from registration.backends.simple.views import RegistrationView

class ExAuthenticationForm(AuthenticationForm):
    keep_logged = forms.BooleanField(required=False, label="Keep me logged in")


class ExRegistrationForm(RegistrationForm):
    layout = Layout('username',
                    'email',
                    Row('password1', 'password2'))

    # template = Template("""
    # {% form %}
    #     {% part form.username prefix %}<i class="material-icons prefix">account_box</i>{% endpart %}
    #     {% part form.email prefix %}<i class="material-icons prefix">email</i>{% endpart %}
    #     {% part form.password1 prefix %}<i class="material-icons prefix">lock</i>{% endpart %}
    #     {% part form.password2 prefix %}<i class="material-icons prefix">lock</i>{% endpart %}
    # {% endform %}
    # """)

class ExRegistrationView(RegistrationView):
    form_class = ExRegistrationForm