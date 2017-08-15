from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import User
import uuid

'''
[Django API](https://docs.djangoproject.com/en/1.11/)
[Django中null和blank的区别](http://www.tuicool.com/articles/2ABJbmj)
'''



class Page(models.Model):
    COVER = 'cover'
    PROLOGUE = 'prologue'
    PREFACE = 'Preface'
    CATALOG = 'catalog'
    PUBLISH = 'publish'
    BLANK = 'blank'
    CONTENT = 'content'
    TYPE_CHOICES = (
        (COVER, '封面'),
        (PROLOGUE, '序言'),
        (PREFACE, '前言'),
        (CATALOG, '目录'),
        (PUBLISH, '出版页'),
        (BLANK, '空白页'),
        (CONTENT, '内容'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=64, unique=True, db_index=True, verbose_name='编号')
    name = models.CharField(max_length=64, verbose_name='页码')
    type = models.CharField(
        max_length=8,
        choices=TYPE_CHOICES,
        default=CONTENT,
        verbose_name='类型'
    )
    roll_id = models.IntegerField(null=True, blank=True, verbose_name='卷id')
    series = models.CharField(max_length=64, null=True, blank=True, db_index=True, verbose_name='部')
    volume = models.CharField(max_length=64, null=True, blank=True, db_index=True, verbose_name='册')
    sutra = models.CharField(max_length=64, null=True, blank=True, db_index=True, verbose_name='经')
    pre_page = models.CharField(max_length=64, null=True, blank=True, verbose_name='上一页')
    next_page = models.CharField(max_length=64, null=True, blank=True, verbose_name='下一页')


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

class Character(models.Model):
    INITIAL = 'initial'
    DONE = 'done'
    RECOG = 'recog'
    MANUAL = 'manual'
    STATE_CHOICES = (
        (DONE, '已完成'),
        (RECOG, '已识别'),
        (MANUAL, '已人工处理'),
        (INITIAL, '待处理'),
    )
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    page = models.ForeignKey(Page, related_name='characters', on_delete=models.CASCADE, verbose_name='页')
    org = models.CharField(u'原字', max_length=4, db_index=True)
    hans = models.CharField(u'正字', max_length=4, db_index=True)
    x1 = models.SmallIntegerField(u'左上x')
    y1 = models.SmallIntegerField(u'左上y')
    x2 = models.SmallIntegerField(u'右下x')
    y2 = models.SmallIntegerField(u'右下y')
    bottom = models.SmallIntegerField(u'下')
    line_no = models.SmallIntegerField(u'行号')
    char_no = models.SmallIntegerField(u'字号')
    region_no = models.SmallIntegerField(u'区号', default=0)
    confidence = models.SmallIntegerField(u'置信度', default=0, db_index=True)
    state = models.CharField(max_length=2, choices=STATE_CHOICES, default=INITIAL, verbose_name='处理状态')

class BatchVersion(models.Model, UsableStatus):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organiztion = models.CharField(null=True, blank=True, verbose_name='组织名称', max_length=128)
    submit_date = models.DateTimeField(null=True, blank=True, verbose_name='提交日期', auto_now_add = True)
    accepted = models.PositiveSmallIntegerField('状态', choices=UsableStatus.STATUS,
            default=UsableStatus.UNUSABLE, db_index=True)

class CutBatchOP(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    batch_version = models.ForeignKey(BatchVersion, blank=True, null=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    page = models.ForeignKey(Page, blank=True, null=True, related_name='character_ops', on_delete=models.CASCADE, verbose_name='页')
    x1 = models.SmallIntegerField('左上x')
    y1 = models.SmallIntegerField('左上y')
    x2 = models.SmallIntegerField('右下x')
    y2 = models.SmallIntegerField('右下y')
    submit_date = models.DateTimeField(null=True, blank=True, verbose_name='提交日期', auto_now = True)
