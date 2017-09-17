from __future__ import absolute_import
from django.utils.translation import ugettext as _
import xadmin
from xadmin import views
from .models import Page, OPage, CutBatchOP
from .models import BatchVersion as BV
from xadmin.layout import Main, TabHolder, Tab, Fieldset, Row, Col, AppendedText, Side
from xadmin.plugins.inline import Inline
from xadmin.plugins.batch import BatchChangeAction
from django import forms
from datetime import date
import oss2
import os,zipfile,base64,math,json
from oss import get_oss_by_name
from lqcharacter.settings import UPLOAD


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
            {"type": "addform", "model": BV},
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

def is_img_exist(image_name):
    auth = oss2.Auth(os.environ.get('OSS_API_KEY'), os.environ.get('OSS_API_SECRET'))
    bucket = oss2.Bucket(auth, 'oss-cn-shanghai.aliyuncs.com', 'tripitaka')
    return bucket.object_exists(get_oss_by_name(image_name))

def put_zip_into_db(batch_version, zip_path):
    img_not_exist = []
    opage_list = []
    page_list = []
    data_list = []
    zfile = zipfile.ZipFile(zip_path, 'r')
    # TODO 要和用户约定上传文件格式
    for i in zfile.namelist()[1:]:
        name = i.split('.')
        img_name = name[0].split("/")[-1]
        if is_img_exist(img_name+'.png') or is_img_exist(img_name+'.jpg'):
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
                                "hans":"",
                            }
                            # 每行一个json
                        )
                json_str = json.dumps(d)
                b64 = base64.b64encode(json_str.encode('utf-8'))
                opage = OPage.objects.filter(img_name + name[-2])
                if opage:
                    opage = opage[0]
                else:
                    opage = OPage(name=img_name + name[-2], md5="")
                p = Page(batch_version=batch_version, image=opage)
                c = CutBatchOP(page=p, cut_data=b64)
                opage_list.append(opage)
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
    upload_field = forms.FileField(required=False, label='ZIP文件', max_length=128, widget=forms.FileInput(attrs={'accept':'application/zip'}))

    def save(self, commit=True):
        upload_field = self.cleaned_data.get('upload_field', None)
        #b = BV(organiztion=upload_field.name.split("_")[0],des=self.data['des'])
        b = BV(organiztion=1,des=self.data['des'])
        b.save()
        zip_up = put_zip_into_db(b, upload_field)
        #TODO 与贤颠法师确认如何生成BatchVersion
        # ...do something with upload_field here...
        return super(BatchVersionModelForm, self).save(commit=commit)

    class Meta:
        fields = ('organiztion', 'now_date', 'upload_field', 'des')
        model = BV


@xadmin.sites.register(BV)
class BatchVersion(object):
    form = BatchVersionModelForm

    fieldsets = (
        (None, {
            'fields': ('organiztion', 'now_date', 'upload_field', 'des'),
        }),
    )
    pass
