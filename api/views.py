#-*- encoding=utf8 -*-
from rest_framework import viewsets
from .serializers import BatchVersionSerializer, CutBatchOPSerializer, PageSerializer, OPageSerializer
from core.models import CutBatchOP,BatchVersion,Page,OPage

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
        img_path = p.get_image_url
        img = Image.open(io.BytesIO(urllib.request.urlopen(img_path).read()))
        image = img.crop((x,y,x+width,y+height))
        buffer = io.BytesIO()
        image.save(buffer, format="png")
        img_str = base64.b64encode(buffer.getvalue())
        #Image.open(io.BytesIO(base64.b64decode(str)))
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
        if page.final == 0:
            page.final = 1
        elif page.final == 1:
            page.final = 2
        page.save()
        page.image.final = True
        page.image.save()
        return Response({
            "id":pk,
            "code":page.image_name,
            "image_url":page.get_image_url,
            "jsondata":page.c_page.first().cut_data
            })

    @detail_route(methods=['get'], url_path='get_final')
    def get_final(self):
        return Page.objects.filter(final__gt=0)




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

    @detail_route(methods=['post'], url_path='finish_verify')
    def finish_verify(self,request,pk):
        #完成校对
        cut_data_pack = request.data
        cut = CutBatchOP.objects.get(pk=pk)
        cut.cut_data = cut_data_pack
        cut.save()
        if cut.page.final == 0:
            cut.page.final = 1
        elif cut.page.final == 1:
            cut.page.final = 2
        cut.page.save()
        cut.page.image.final = True
        cut.page.image.save()
        return Response(CutBatchOPSerializer(cut).data)

def compare_file(filea, fileb):
    return hashlib.md5(base64.b64encode(open(filea,'rb').read())).digest() == hashlib.md5(base64.b64encode(open(fileb,'rb').read())).digest()

class BatchVersionViewSet(viewsets.ModelViewSet):
    serializer_class = BatchVersionSerializer
    queryset = BatchVersion.objects.all()

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

