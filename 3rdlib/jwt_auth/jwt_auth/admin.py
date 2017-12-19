# coding: utf-8


from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import Staff


class StaffCreationForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Staff
        fields = ('email', 'realname')

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('密码不正确')
        return password2

    def save(self, commit=True):
        staff = super(StaffCreationForm, self).save(commit=False)
        staff.set_password(self.cleaned_data['password1'])
        if commit:
            staff.save()
        return staff


class StaffChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = Staff
        fields = ('email', 'password', 'realname')

    def clean_password(self):
        return self.initial['password']


class StaffAdmin(BaseUserAdmin):
    form = StaffChangeForm
    add_form = StaffCreationForm

    list_display = ('email', 'is_admin')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('email', 'realname', 'password')}),
        ('Personal info', {'fields': ('last_login',)}),
        ('Permissions', {'fields': ('is_admin',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'last_login', 'password1', 'password2')}
         ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()


# Now register the new UserAdmin
admin.site.register(Staff, StaffAdmin)
admin.site.unregister(Group)
