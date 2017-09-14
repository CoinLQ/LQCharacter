from __future__ import absolute_import
from django.utils.translation import ugettext as _
import xadmin
from xadmin import views
from .models import Page, BatchVersion
from xadmin.layout import Main, TabHolder, Tab, Fieldset, Row, Col, AppendedText, Side
from xadmin.plugins.inline import Inline
from xadmin.plugins.batch import BatchChangeAction
from django import forms
from datetime import date


@xadmin.sites.register(views.website.IndexView)
class MainDashboard(object):
    title = _("欢迎使用切分系统")
    icon = "fa fa-dashboard"
    widgets = [
        [
            {"type": "html", "title": "欢迎语",
             "content": "<h3> 欢迎! </h3><p>切分与识别！ <br/>加入我们，@longquan</p>"},
            {"type": "chart", "model": "core.page", "chart": "user_count",
             "params": {"_p_date__gte": "2013-01-08", "p": 1, "_p_date__lt": "2013-01-29"}},
            {"type": "list", "model": "core.page", "params": {"o": "-id"}},
        ],
        [
            {"type": "qbutton", "title": "快捷方式",
             "btns": [{"model": BatchVersion}]},
            {"type": "addform", "model": BatchVersion},
        ]
    ]


@xadmin.sites.register(views.BaseAdminView)
class BaseSetting(object):
    enable_themes = True
    use_bootswatch = False


@xadmin.sites.register(views.CommAdminView)
class GlobalSetting(object):
    global_search_models = [ Page ]
    site_title = "切分后台管理系统"
    site_footer = "@longquan"
    menu_style = 'default'  # 'accordion'


@xadmin.sites.register(Page)
class PageAdmin(object):
    pass



class BatchVersionModelForm(forms.ModelForm):


    now_date = forms.DateField(label='日期', initial=date.today, disabled=True)
    upload_field = forms.FileField(label='ZIP文件', max_length=128, widget=forms.FileInput(attrs={'accept':'application/zip'}))

    def save(self, commit=True):
        upload_field = self.cleaned_data.get('upload_field', None)
        # ...do something with upload_field here...
        return super(BatchVersionModelForm, self).save(commit=commit)

    class Meta:
        fields = ('organiztion', 'now_date', 'upload_field', 'des')
        model = BatchVersion


@xadmin.sites.register(BatchVersion)
class BatchVersion(object):
    form = BatchVersionModelForm

    fieldsets = (
        (None, {
            'fields': ('organiztion', 'now_date', 'upload_field', 'des'),
        }),
    )
    pass
