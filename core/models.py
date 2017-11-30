# -*- coding: utf-8 -*-
from django.db import models

# Create your models here.

from django.contrib.auth.models import User
from django.template import defaultfilters
from django.dispatch import receiver
import base64
import json
import os
import uuid
import sys
import urllib.request
import functools
import db_file_storage
from PIL import Image, ImageFont, ImageDraw
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.validators import MaxValueValidator, MinValueValidator
from io import BytesIO
from db_file_storage.model_utils import delete_file, delete_file_if_needed
from dotmap import DotMap
from lqcharacter import settings
from django.db import transaction
from lib.arrange_rect import ArrangeRect
from lib.utils import timeit
from django.utils.timezone import now

# [Django API](https://docs.djangoproject.com/en/1.11/)

db_storage = db_file_storage.storage.DatabaseFileStorage()


def default_today():
    return now().today()


def iterable(cls):
    """
    model的迭代器并输出dict，且不包含内部__,_开头的key
    """
    @functools.wraps(cls)
    def iterfn(self):
        iters = dict((k, v) for k, v in self.__dict__.items() if not k.startswith("_"))

        for k, v in iters.items():
            yield k, v

    cls.__iter__ = iterfn
    return cls


class UsableStatus(object):
    UNUSABLE = 0
    USABLE = 1
    DELETED = 99
    STATUS = (
        (UNUSABLE, u'不可用'),
        (USABLE, u'启用'),
        (DELETED, u'删除'),
    )


class ORGGroup(object):
    ALI = 0
    BAIDU = 1
    SKY = 2
    IDS = (
        (ALI, u'阿里'),
        (BAIDU, u'百度'),
        (SKY, u'社科院'),
    )


class FinalStatus(object):
    INIT = 0
    FIRSTCHECK = 1
    TWICECHECK = 2
    STATUS = (
        (INIT, u'新入库'),
        (FIRSTCHECK, u'已初校'),
        (TWICECHECK, u'已二校'),
    )


class RectStatus(object):
    INIT = 0
    NEW_ADD = 1
    MODIFIED = 2
    DELETED = 3
    DONE = 4
    STATUS = (
        (INIT, u'新入库'),
        (NEW_ADD, u'新增'),
        (MODIFIED, u'已修改'),
        (DELETED, u'已删除'),
        (DONE, u'已处理'),
    )


class BatchVersion(models.Model, UsableStatus, ORGGroup):
    class Meta:
        verbose_name = u'版本批次'
        verbose_name_plural = u"版本批次管理"
        ordering = ('-submit_date', )

    class Config:
        list_display_fields = ('id', 'organiztion', 'submit_date', 'des', 'accepted', 'upload_field')
        list_form_fields = list_display_fields
        search_fields = list_display_fields

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organiztion = models.PositiveSmallIntegerField(verbose_name=u'组织名称', choices=ORGGroup.IDS,
            default=ORGGroup.ALI)
    submit_date = models.DateTimeField(null=True, blank=True, verbose_name=u'提交日期', auto_now_add = True)
    des = models.TextField(verbose_name=u'描述', null=True, blank=True, max_length= 128)
    accepted = models.PositiveSmallIntegerField(u'状态', choices=UsableStatus.STATUS,
            default=UsableStatus.UNUSABLE, db_index=True)
    upload_field = models.FileField(null=True, blank=True, upload_to="", verbose_name=u"zip文件")


    def __str__(self):
        return '%s: %s' % (ORGGroup.IDS[int(self.organiztion)][1],
                           defaultfilters.date(self.submit_date, "SHORT_DATE_FORMAT"))


class OPage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128, blank=True, null=True)
    final = models.BooleanField(default=False)
    md5 = models.CharField(max_length=32, db_index=True)

    def __str__(self):
        return self.name


class Page(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    batch_version = models.ForeignKey(BatchVersion, blank=True, null=True, on_delete=models.CASCADE,
                                      related_name="page_batchversion")
    image = models.ForeignKey(OPage)
    final = models.SmallIntegerField(verbose_name=u'校对情况', choices=FinalStatus.STATUS, default=0)
    created_at = models.DateTimeField(u'创建于', null=True, blank=True, auto_now_add=True)
    temp_image = models.FileField(u'临时图片', null=True, blank=True, help_text=u's3本地缓存', upload_to='tmp/')
    updated_at = models.DateTimeField(u'更新于', null=True, blank=True, auto_now=True)
    locked = models.SmallIntegerField(verbose_name=u'锁定状态', default=0, db_index=True)
    text_info = models.TextField(u'识别文字信息', blank=True, null=True)

    class Meta:
        verbose_name = u'页'
        verbose_name_plural = u"页面管理"
        ordering = ('-created_at', )

    class Config:
        list_display_fields = ('id', 'batch_version', 'created_at', 'image', 'final')
        list_form_fields = list_display_fields
        search_fields = list_display_fields

    @property
    def image_name(self):
        return self.image.name

    @property
    def image_md5(self):
        return self.image.md5

    @property
    def get_image_url(self):
        # return os.path.join(settings.IMAGE_ROOT, self.image.name)
        # from oss import get_oss_by_name
        # return "http://tripitaka.oss-cn-shanghai.aliyuncs.com/" + get_oss_by_name(self.image.name)
        return "https://s3.cn-north-1.amazonaws.com.cn/lqcharacters-images/" + self.image.name

    def __str__(self):
        return self.image_name

    @timeit
    def rebuild_rect(self):
        self.rects.all().delete()
        if self.c_page.first().cut_data.strip() == '':
            return
        json_str = base64.b64decode(self.c_page.first().cut_data)
        cut_result = json.loads(json_str.decode('utf-8'))
        # image = self._remote_image_stream()
        for _m in cut_result:
            m = DotMap(_m)
            if m.op != 3:
                # rect = Rect.objects.create(page=self, x=m.x, y=m.y, width=int(m.width),
                #               height=int(m.height),confidence=m.confidence, op=m.op, hans=m.hans)
                # rect.feed_image2DB(image)
                if (int(m.width) < 0) or (int(m.height) < 0):
                    continue
                Rect.objects.create(page=self, x=m.x, y=m.y, width=int(m.width), height=int(m.height),
                                    confidence=m.confidence, op=m.op, hans=m.hans)


    @timeit
    def reformat_rects(self):
        columns, column_len = ArrangeRect.resort_rects_from_qs(self.rects.exclude(op=3))
        with transaction.atomic():
            for lin_n, line in columns.items():
                for col_n, col in enumerate(line):
                    rect = DotMap(col)
                    Rect.objects.filter(pk=rect.id).update(line_no=lin_n, col_no =col_n + 1)

    def _remote_image_stream(self):
        opener = urllib.request.build_opener()
        # AWS S3 Private Resource snippet, someday here should to be.
        # opener.addheaders = [('Authorization', 'AWS AKIAIOSFODNN7EXAMPLE:02236Q3V0RonhpaBX5sCYVf1bNRuU=')]
        reader = opener.open(self.get_image_url)
        return Image.open(BytesIO(reader.read()))

    def make_annotate(self, columns):
        source_img = self._remote_image_stream().convert("RGBA")
        work_dir = "/tmp/annotations"
        try:
            os.stat(work_dir)
        except:
            os.makedirs(work_dir)
        out_file = "%s/%s.jpg" % (work_dir, self.image_name)
        # make a blank image for the rectangle, initialized to a completely transparent color
        tmp = Image.new('RGBA', source_img.size, (0, 0, 0, 0))
        # get a drawing context for it
        draw = ImageDraw.Draw(tmp)
        if sys.platform in ('linux2', 'linux'):
            myfont = ImageFont.truetype(settings.BASE_DIR + "/static/fonts/SourceHanSerifTC-Bold.otf", 11)
        elif sys.platform == 'darwin':
            myfont = ImageFont.truetype("/Library/Fonts/Songti.ttc", 12)

        for lin_n, line in columns.items():
            for col_n, col in enumerate(line):
                rect = DotMap(col)
                # draw a semi-transparent rect on the temporary image
                draw.rectangle(((rect.x, rect.y), (rect.x + int(rect.width), rect.y + int(rect.height))),
                                 fill=(0, 0, 0, 120))
                anno_str = u"%s-%s" % (lin_n, col_n + 1)
                draw.text((rect.x, rect.y), anno_str, font=myfont, fill=(200, 255, 255))
        source_img = Image.alpha_composite(source_img, tmp)
        source_img.save(out_file, "JPEG")


class CutBatchOP(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    page = models.ForeignKey(Page, blank=True, null=True, on_delete=models.CASCADE, related_name="c_page")
    cut_data = models.TextField(blank=True, null=True)
    submit_date = models.DateTimeField(null=True, blank=True, verbose_name=u'提交日期', auto_now = True)

    def __str__(self):
        return '%s: %s' % (self.id, self.cut_data)


class DBPicture(models.Model):
    bytes = models.TextField()
    filename = models.CharField(max_length=255)
    mimetype = models.CharField(max_length=50)


class SplitTask(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    confidence = models.FloatField(u'置信度', default=1, db_index=True)
    owner = models.ForeignKey(User, null=True, blank=True, default=None)
    locked = models.SmallIntegerField(verbose_name=u'锁定状态', default=0, db_index=True)
    groups = []

    class Meta:
        ordering = ('confidence', )

    @classmethod
    def assign(cls, user):
        pass

    @classmethod
    def create_tasks(cls, base_confidence, block_size=50):
        for rect in Rect.objects.filter(split_task=None,
                                        confidence__lte=base_confidence).order_by('confidence'):
            SplitTask.create_split_task_group(rect, block_size)

    @classmethod
    def create_split_task_group(cls, rect, block_size):
        SplitTask.groups.append(rect)
        groups = SplitTask.groups
        if len(groups) == block_size:
            average = sum([x.confidence for x in groups]) / len(groups)
            split_task = SplitTask.objects.create(confidence=average)
            ids = list(map(lambda x: x.id, groups))
            Rect.objects.filter(id__in=ids).update(split_task=split_task)
            SplitTask.groups.clear()


@iterable
class Rect(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    line_no = models.PositiveSmallIntegerField(u'行号', default=0)  # 旋转90度观想，行列概念
    col_no = models.PositiveSmallIntegerField(u'列号', default=0)
    x = models.PositiveSmallIntegerField(u'X坐标', default=0)
    y = models.PositiveSmallIntegerField(u'Y坐标', default=0)
    width = models.PositiveSmallIntegerField(u'Y坐标', default=1,
            validators=[MinValueValidator(1), MaxValueValidator(300)])
    height = models.PositiveSmallIntegerField(u'Y坐标', default=1,
             validators=[MinValueValidator(1), MaxValueValidator(300)])
    confidence = models.FloatField(u'置信度', default=1, db_index=True)
    op = models.PositiveSmallIntegerField(u'类型', default=RectStatus.INIT, db_index=True)
    hans = models.CharField(u'汉字', max_length=4, default='')
    page = models.ForeignKey(Page, blank=True, null=True, on_delete=models.CASCADE, related_name="rects")
    split_task = models.ForeignKey(SplitTask, blank=True, null=True, on_delete=models.CASCADE,
                                   related_name="rects")
    inset = models.FileField(null=True, blank=True, help_text=u'嵌入临时截图',
                             upload_to='core.DBPicture/bytes/filename/mimetype',
                             storage=db_storage)
    s3_inset = models.FileField(u's3地址', blank=True, null=True, upload_to='tripitaka/hans',
                                storage='storages.backends.s3boto.S3BotoStorage')

    class Meta:
        indexes = [
            models.Index(fields=['page', 'line_no']),
        ]
        ordering = ('-confidence', )

    def feed_image2DB(self, image):
        buffer = BytesIO()
        with image.crop((self.x, self.y, self.x + self.width, self.y + self.height)) as f:
            f.save(buffer, format="png")
        feed_image = ContentFile(buffer.getvalue())
        image_file = InMemoryUploadedFile(feed_image, None, "%s.png" % self.id, 'image/png',
                                          feed_image.tell, None)
        self.inset = image_file
        self.save()

    def save(self, *args, **kwargs):
        delete_file_if_needed(self, 'inset')
        super(Rect, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super(Rect, self).delete(*args, **kwargs)
        delete_file(self, 'inset')

    @property
    def inset_uri(self):
        # if not self.inset:
        #     image = self.page._remote_image_stream()
        #     self.feed_image2DB(image)
        return "/files/get/?name=core.DBPicture/bytes/filename/mimetype/%s.png" % self.id

    @property
    def inset_datauri(self):
        if not self.inset:
            image = self.page._remote_image_stream()
            self.feed_image2DB(image)
        return "/files/get/?name=core.DBPicture/bytes/filename/mimetype/%s.png" % self.id


class Profile(models.Model):
    user = models.OneToOneField(User)
    sex_type = (('male', u'男'), ('female', u'女'))
    sex = models.CharField(u"性别", choices=sex_type, default='male', max_length=32)
    birthday = models.DateField(u'出生日期', max_length=64, blank=True, null=True, help_text="格式yyyy-mm-dd")
    phone = models.BigIntegerField(u'手机号', blank=True, null=True)
    id_num = models.CharField(u'身份证号', blank=True, null=True, max_length=64)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    rects = models.ManyToManyField(Rect, through='RectSubscription')
    pages = models.ManyToManyField(Page, through='PageSubscription')

    @property
    def today_rects(self):
        return self.rects.filter(date=default_today()).all()

    @property
    def today_page(self):
        return self.pages.filter(date=default_today()).all()


class RectSubscription(models.Model):
    profile = models.ForeignKey(Profile, db_constraint=True, db_index=False)
    rect = models.ForeignKey(Rect, db_constraint=True, db_index=False, null=True, on_delete=models.SET_NULL)
    date = models.DateField(default=default_today)
    op_type = (('add', u'增加'), ('modify', u'修改'), ('delete', u'删除'))
    op = models.CharField(u"操作类型", choices=op_type, default='modify', max_length=8)

    class Meta:
        db_table = 'rects_user_profile_rects'
        index_together = (("profile", "date", "rect"),)

    def __str__(self):
        return u'Subscription for %s to %s' % (
            self.profile.user.email, self.rect.id)

    @classmethod
    def rect_creation_log(cls, profile, rect):
        if not RectSubscription.objects.filter(profile=profile, rect=rect, date=default_today):
            RectSubscription.objects.create(profile=profile, rect=rect, op='add')

    @classmethod
    def rect_modification_log(cls, profile, rect):
        if not RectSubscription.objects.filter(profile=profile, rect=rect, date=default_today):
            RectSubscription.objects.create(profile=profile, rect=rect, op='modify')

    @classmethod
    def rect_deletion_log(cls, profile, rect):
        RectSubscription.objects.create(profile=profile, rect=rect, op='delete')


class PageSubscription(models.Model):
    profile = models.ForeignKey(Profile, db_constraint=True, db_index=False)
    page = models.ForeignKey(Page, db_constraint=True, db_index=False)
    date = models.DateField(default=default_today)
    op_type = (('add', u'增加'), ('modify', u'修改'), ('delete', u'删除'))
    op = models.CharField(u"操作类型", choices=op_type, default='modify', max_length=8)

    class Meta:
        db_table = 'pages_user_profile_pages'
        unique_together = (("profile", "page", "date"),)

    def __str__(self):
        return u'Subscription for %s to %s' % (
            self.profile.user.email, self.page.image_name)


@receiver(models.signals.post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
