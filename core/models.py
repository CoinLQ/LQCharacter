# -*- encoding:utf8 -*-
from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import User
import uuid
from django.shortcuts import render
from lqcharacter import settings
import os
#[Django API](https://docs.djangoproject.com/en/1.11/)
#[Django中null和blank的区别](http://www.tuicool.com/articles/2ABJbmj)

## 切分业务模型设计
class UsableStatus(object):
    UNUSABLE = 0
    USABLE = 1
    DELETED = 99
    STATUS = (
        (UNUSABLE, u'不可用'),
        (USABLE, u'启用'),
        (DELETED, u'删除'),
    )

class BatchVersion(models.Model, UsableStatus):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    des = models.TextField(verbose_name=u'描述',null=True, blank=True)
    organiztion = models.CharField(null=True, blank=True, verbose_name=u'组织名称', max_length=128)
    submit_date = models.DateTimeField(null=True, blank=True, verbose_name=u'提交日期', auto_now_add = True)
    accepted = models.PositiveSmallIntegerField(u'状态', choices=UsableStatus.STATUS,
            default=UsableStatus.UNUSABLE, db_index=True)

class OPage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128, blank=True, null=True)
    final = models.BooleanField(default=False)
    md5 = models.CharField(max_length=128, Index=True)

class Page(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    batch_version = models.ForeignKey(BatchVersion, blank=True, null=True, on_delete=models.SET_NULL)
    image = models.ForeignKey(OPage)

    @property
    def image_name(self):
        return self.image.name

    @property
    def get_image_url(self):
        #return os.path.join(settings.IMAGE_ROOT, self.image.name)
        return "http://ac-hsnl7zbi.clouddn.com/wlQMt4GhJs8afpwuWWvmRJoG61mJiTPmiqve6yJH.jpg"

    @property
    def get_page_url(self):
        return "http://127.0.0.1:8000/"+str(self.id)

class CutBatchOP(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    page = models.ForeignKey(Page, blank=True, null=True, on_delete=models.SET_NULL, related_name="c_page")
    cut_data = models.TextField(blank=True,null=True)
    submit_date = models.DateTimeField(null=True, blank=True, verbose_name=u'提交日期', auto_now = True)

    def __unicode__(self):
        return '%s: %s' % (self.id, self.cut_data)
