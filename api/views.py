#-*- encoding=utf8 -*-
from rest_framework import viewsets
from .serializers import BatchVersionSerializer, CutBatchOPSerializer, PageSerializer, OPageSerializer
from core.models import CutBatchOP,BatchVersion,Page,OPage
import os
from rest_framework.decorators import list_route, detail_route
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
import base64
from PIL import Image
import io
from rest_framework import generics
from django.db.models import Q
import hashlib
import urllib
import re
import oss2

class PageViewSet(viewsets.ModelViewSet):
    serializer_class = PageSerializer
    queryset = Page.objects.all()
    permission_classes = (AllowAny,)

    @detail_route(methods=["post"], url_path="pre_image")
    def pre_image(self, request, pk):
        data = request.data
        page_id = pk
        x = data['x']
        y = data['y']
        width = data['width']
        height = data['height']
        p = Page.objects.get(pk=page_id)
        img_path = p.get_image_url()
        if re.match(re.compile(
                {r'^(?:http|ftp)s?:(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
                 r'localhost|'  # localhost...
                 r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                 r'(?::\d+)?'  # optional port
                 r'(?:/?|[/?]\S+)$'}, re.IGNORECASE),img_path):
            img = io.BytesIO(urllib.request.urlopen(img_path).read())
        else:
            img = Image.open(img_path)
        image = img.crop((x,y,x+width,y+height))
        buffer = io.BytesIO()
        image.save(buffer, format="png")
        img_str = base64.b64encode(buffer.getvalue())

        return Response(img_str)

    @detail_route(methods=["get"],url_path="one")
    def get_one_page(self,request,pk):
        pk = pk
        page = Page.objects.get(pk=pk)
        #{"id":"","code":"","image_url":"","json_data":""}
        b64 = page.c_page.first().cut_data
        s = base64.b64decode(b64)
        return Response(
            {
                "id":pk,
                "code":page.image_name,
                "image_url":page.get_image_url,
                "jsondata":page.c_page.first().cut_data
            })

    @detail_route(methods=["get"], url_path="next")
    def get_next_page(self,request,pk):
        pk = pk
        page = Page.objects.exclude(pk=pk).first()
        b64 = page.c_page.first().cut_data
        s = base64.b64decode(b64)
        return Response(
            {
                "id":page.id,
                "code":page.image_name,
                "image_url":page.get_image_url,
                "jsondata":page.c_page.first().cut_data
            })


    @detail_route(methods=['post'],  url_path='save_op')
    def save_op(self, request, pk):
        page = Page.objects.get(pk=pk)
        c = page.c_page.first()
        s = base64.b64decode(request.data['jsondata'])
        c.cut_data = request.data['jsondata']
        c.save()

        page.image.final = True
        page.image.save()
        return Response({
            "id":pk,
            "code":page.image_name,
            "image_url":page.get_image_url,
            "jsondata":page.c_page.first().cut_data
            })

class FinalPageViewSet(generics.ListAPIView):
    serializer_class = PageSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        return Page.objects.filter(Q(image__final=True)|(Q(batch_version__accepted=2)&Q(image__final=False)))

class CutBatchOPViewSet(viewsets.ModelViewSet):
    serializer_class = CutBatchOPSerializer
    queryset = CutBatchOP.objects.all()
    #permission_classes = (AllowAny,)

    @detail_route(methods=['post'], url_path='submit_cut_64')
    def sub_64(self, request, pk):
        cut_data_pack = request.data
        cut = CutBatchOP.objects.get(pk=pk)
        cut.cut_data = cut_data_pack
        cut.save()
        return Response(CutBatchOPSerializer(cut).data)

def put_json_into_db(batch_version, json_path):
    opage_list = []
    page_list = []
    data_list = []
    for json_file in os.listdir(json_path):
        if json_file.split(".")[-1] == 'base64':
            with open(json_path + json_file) as json_data:
                opage = OPage(name = json_file.split(".")[0]+".jpg", md5="")
                p = Page(batch_version= batch_version, image = opage)
                c = CutBatchOP(page=p,cut_data=json_data.read())
                opage_list.append(opage)
                page_list.append(p)
                data_list.append(c)
    OPage.objects.bulk_create(opage_list)
    Page.objects.bulk_create(page_list)
    CutBatchOP.objects.bulk_create(data_list)

def UploadImage(local_path):
    auth = oss2.Auth(os.environ.get('OSS_API_KEY'), os.environ.get('OSS_API_SECRET'))
    bucket = oss2.Bucket(auth, 'oss-cn-shanghai.aliyuncs.com', 'tripitaka')
    filelist = os.listdir(local_path)
    for file_ele in filelist:
        if file_ele.split(".")[-1] == 'jpg':
            bucket.put_object_from_file('lqhansp/' + file_ele, local_path + file_ele)

local_path = '/data/share/dzj_characters/images/'


def compare_file(filea, fileb):
    return hashlib.md5(base64.b64encode(open(filea,'rb').read())).digest() == hashlib.md5(base64.b64encode(open(fileb,'rb').read())).digest()

class BatchVersionViewSet(viewsets.ModelViewSet):
    serializer_class = BatchVersionSerializer
    queryset = BatchVersion.objects.all()
    permission_classes = (AllowAny,)

    @list_route(methods=['get'], url_path='bulkcreate')
    def batch_import(self, request):
        os.system("ruby /home/buddhist/AI/QIEZI/process.rb " + local_path)
        b = BatchVersion(des="batch_v_1", organiztion='lqs')
        b.save()
        put_json_into_db(b, local_path)
        UploadImage(local_path)
        #put_json_into_db(b, "/home/buddhist/AI/QIEZI")
        return Response({'status': 'ok'})

    @detail_route(methods='get', url_path='switch_status')
    def switch_status(self, request, pk):
        batch_version = BatchVersion.objects.get(pk=pk)
        new_status = request.data['status']
        if new_status == 3:
            batch_version.accepted = 3
        if new_status == 2:
            batch_version = 2
        #TODO TBD


class OPageViewSet(viewsets.ModelViewSet):
    serializer_class = OPageSerializer
    queryset = OPage.objects.all()

