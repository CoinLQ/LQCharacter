#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

'''
Created by zhaopan on 2017/10/30.
'''

__author__ = 'zhaopan'

from django.template import Template
from material import Layout, Row
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import PasswordChangeForm
from registration.forms import RegistrationForm
from registration.backends.simple.views import RegistrationView
from accounts.urls import common_form_template
from django import forms
from core.models import Profile
from django.forms import ModelForm



class ExAuthenticationForm(AuthenticationForm):
    keep_logged = forms.BooleanField(required=False, label="保持登录")  # Keep me logged in
    template = Template('''
    {% form %}
        {% part form.username prefix %}<i class="material-icons prefix">account_box</i>{% endpart %}
        {% part form.password prefix %}<i class="material-icons prefix">lock</i>{% endpart %}
        {% attr form.keep_logged 'group' class append %}right-align{% endattr %}
    {% endform %}
    ''')
    buttons = Template('''
        {% load i18n %}
        <a class="waves-effect waves-light btn-flat"
            href="{% url 'registration_register' %}">{% trans 'Register' %}</a>
        <button class="waves-effect waves-light btn" type="submit">{% trans 'Log in' %}</button>
    ''')


class ExRegistrationForm(RegistrationForm):
    layout = Layout('username',
                    'email',
                    Row('password1', 'password2'))
    title = 'Register'
    template = Template("""
    {% form %}
        {% part form.username prefix %}<i class="material-icons prefix">account_box</i>{% endpart %}
        {% part form.email prefix %}<i class="material-icons prefix">email</i>{% endpart %}
        {% part form.password1 prefix %}<i class="material-icons prefix">lock</i>{% endpart %}
        {% part form.password2 prefix %}<i class="material-icons prefix">lock</i>{% endpart %}
    {% endform %}
    """)
    buttons = Template('''
        {% load i18n %}
        <button type="submit" name="_submit" class="btn btn-primary btn-lg">{% trans 'Submit' %}</button>
    ''')


class ExRegistrationView(RegistrationView):
    form_class = ExRegistrationForm
    template_name = common_form_template


class ExPasswordChangeForm(PasswordChangeForm):
    layout = Layout('old_password', Row('new_password1', 'new_password2'))
    title = 'Password change'
    template = Template("""
    {% form %}
        {% part form.old_password prefix %}<i class="material-icons prefix">lock</i>{% endpart %}
        {% part form.new_password1 prefix %}<i class="material-icons prefix">lock</i>{% endpart %}
        {% part form.new_password2 prefix %}<i class="material-icons prefix">lock</i>{% endpart %}
    {% endform %}
    """)
    buttons = Template('''
        {% load i18n %}
        <button type="submit" name="_submit" class="btn btn-primary btn-lg">{% trans 'Submit' %}</button>
    ''')


class UserProfileChangeForm(ModelForm):
    error_css_class = 'error'
    required_css_class = 'required'
    
    class Meta:
        model = Profile
        fields = ('sex', 'birthday', 'phone', 'id_num')

    layout = Layout(Row('sex', 'birthday'),
                    Row('phone', 'id_num'),)
    
    buttons = Template('''
        {% load i18n %}
        <button type="submit" name="_submit" class="btn btn-primary btn-lg">{% trans 'Submit' %}</button>
    ''')
