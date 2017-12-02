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
            <div class="form register">
                <div class="hd">
                    <img class="l" src="/static/images/registration/lline-v1.png" alt="">
                    <h3><img src="/static/images/registration/resg-v1.png" alt=""></h3>
                    <img class="r" src="/static/images/registration/rline-v1.png" alt="">
                </div>
                <div class="bd">
                    <div class="item">
                        <input id="id_username" maxlength="150" name="username" type="text" autofocus="" value="" placeholder="请输入您的用户名">
                    </div>
                    <div class="item">
                        <input id="id_email" name="email" type="email" value="" placeholder="请输入您的邮箱">
                    </div>
                    <div class="item">
                        <input class="invalid" id="id_password1" name="password1" type="password" value="" placeholder="请输入您的密码">
                    </div>
                    <div class="item">
                        <input class="invalid" id="id_password2" name="password2" type="password" value="" placeholder="请重复你的密码">
                    </div>
                    <div class="item clearfix">
                        <p><span class="fl">重置密码</span><span class="fr">已有账号?&nbsp;点我<a href="/accounts/login/"><em>登录</em></a></span></p>
                    </div>
                </div>
                <button class="btn" type="submit"><img src="/static/images/registration/btn-v1.png" alt=""></button>
            </div>
        </div>
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
