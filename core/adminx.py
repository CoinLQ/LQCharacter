# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.utils.translation import ugettext as _
import xadmin
from xadmin import views
from .models import Page, OPage, CutBatchOP
from .models import BatchVersion as BV
from django import forms
from datetime import date
import oss2
import os
import zipfile
import base64
import math
import json
from oss import get_oss_by_name

import hashlib
from lqcharacter.settings import MEDIA_ROOT
from django.core.files.storage import default_storage


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
             "btns": [{"model": BV}]},
            {"type": "addform", "model": BV}
        ]
    ]


@xadmin.sites.register(views.BaseAdminView)
class BaseSetting(object):
    enable_themes = True
    use_bootswatch = False


@xadmin.sites.register(views.CommAdminView)
class GlobalSetting(object):
    global_search_models = [Page]
    site_title = "切分后台管理系统"
    site_footer = "@longquan"
    menu_style = 'default'  # 'accordion'


@xadmin.sites.register(Page)
class PageAdmin(object):
    list_display = Page.Config.list_display_fields
    list_display_links = ("id")
    search_fields = Page.Config.search_fields


auth = oss2.Auth(os.environ.get('OSS_API_KEY', 'key'), os.environ.get('OSS_API_SECRET', 'pass'))
bucket = oss2.Bucket(auth, 'oss-cn-shanghai.aliyuncs.com', 'tripitaka')


def is_img_exist(image_name):
    return bucket.object_exists(get_oss_by_name(image_name))


def put_zip_into_db(batch_version, zip_path):
    img_not_exist = []
    opage_list = []
    page_list = []
    data_list = []
    zfile = zipfile.ZipFile(zip_path, 'r')
    # TODO 要和用户约定上传文件格式
    for i in zfile.namelist():
        if i.find(".") > -1:
            name = i.split('.')
        else:
            continue
        img_name = name[0].split("/")[-1]
        if is_img_exist(img_name + ".jpg"):
            if name[-1] == 'txt':

                # TODO 需要和用户约定数据文件格式
                data = zfile.read(i)
                a = str(data)
                a = a.replace("b'", "")
                a = a.split('\\n')
                a = [i.split(" ") for i in a]
                d = []
                for ele in a:
                    if len(ele) > 3:
                        d.append(
                            {
                                "x": math.ceil(float((ele[0]))),
                                "y": math.ceil(float((ele[1]))),
                                "width": math.ceil(float((ele[2]))),
                                "height": math.ceil(float((ele[3]))),
                                "confidence": float(ele[4]),
                                "op": 0,
                                "hans": "",
                            }
                            # 每行一个json
                        )
                json_str = json.dumps(d)
                b64 = base64.b64encode(json_str.encode('utf-8'))
                opage = OPage.objects.filter(name=img_name + "." + name[-2])
                if opage:
                    opage = opage[0]
                else:
                    opage = OPage(name=img_name + "." + name[-2], md5="")
                    opage_list.append(opage)
                p = Page(batch_version=batch_version, image=opage)
                c = CutBatchOP(page=p, cut_data=b64)
                page_list.append(p)
                data_list.append(c)
        else:
            img_not_exist.append(name)
    OPage.objects.bulk_create(opage_list)
    Page.objects.bulk_create(page_list)
    CutBatchOP.objects.bulk_create(data_list)
    return img_not_exist


class BatchVersionModelForm(forms.ModelForm):
    now_date = forms.DateField(label='日期', initial=date.today, disabled=True)
    upload_field = forms.FileField(required=True, label='ZIP文件', max_length=128,
                                   widget=forms.FileInput(attrs={'accept': 'application/zip'}))

    def create(self, commit=True):
        pass

    def save(self, commit=True):
        existed = False
        upload_field = self.cleaned_data.get('upload_field', None)
        this_md5 = hashlib.md5(base64.b64encode(upload_field.read())).digest()
        for file in os.listdir(MEDIA_ROOT):
            tmp_md5 = hashlib.md5(base64.b64encode(open(MEDIA_ROOT + file, 'rb').read())).digest()
            if tmp_md5 == this_md5:
                existed = True
                break

        b = self.instance
        b.organiztion = self.data['organiztion']
        b.des = self.data['des']
        b.save()
        if existed:
            pass
        else:
            with default_storage.open(upload_field.name, 'wb+') as destination:
                for chunk in upload_field.chunks():
                    destination.write(chunk)
            put_zip_into_db(b, upload_field)

        return super(BatchVersionModelForm, self).save(commit=commit)

    class Meta:
        fields = ('organiztion', 'now_date', 'upload_field', 'des', 'accepted')
        model = BV


@xadmin.sites.register(BV)
class BatchVersion(object):
    form = BatchVersionModelForm
    fieldsets = (
        (None, {
            'fields': ('organiztion', 'now_date', 'upload_field', 'des', 'accepted'),
        }),
    )
    list_display = BV.Config.list_display_fields
    search_fields = BV.Config.search_fields
