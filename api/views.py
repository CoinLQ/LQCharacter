#-*- encoding=utf8 -*-
from rest_framework import viewsets
from .serializers import BatchVersionSerializer, CutBatchOPSerializer, PageSerializer,PageNSerializer
from core.models import CutBatchOP,BatchVersion,Page
import os
from rest_framework.decorators import list_route, detail_route
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
import base64
from PIL import Image
import io
from rest_framework import generics
from django.db.models import Q


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
        img = Image.open(img_path)
        image = img.crop((x,y,x+width,y+height))
        buffer = io.BytesIO()
        image.save(buffer, format="png")
        img_str = base64.b64encode(buffer.getvalue())

        return Response(img_str)

    @detail_route(methods=["get"], url_path="one")
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
    save_list = []
    for json_file in os.listdir(json_path):
        if json_file.split(".")[-1] == 'base64':
            with open(json_path + '/' + json_file) as json_data:
                p = Page(batch_version= batch_version, image = json_file.split(".")[0])
                c = CutBatchOP(page=p,cut_data=json_data)
                save_list.append(c)
    CutBatchOP.objects.bulk_create(c)

class BatchVersionViewSet(viewsets.ModelViewSet):
    serializer_class = BatchVersionSerializer
    queryset = BatchVersion.objects.all()

    @list_route(methods=['get'], url_path='bulkcreate')
    def batch_import(self, request):
        os.system("ruby /home/buddhist/AI/QIEZI/process.rb /home/buddhist/AI/QIEZI/")
        b = BatchVersion(des="batch_v_1", organiztion='lqs')
        b.save()
        put_json_into_db(b, "/home/buddhist/AI/QIEZI")
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

    '''@list_route(methods=['get'], url_path='fetch_cut_data')
        def fetch(self,request):
            image_name = request.query_params['image']
            cut_datas = CutBatchOPSerializer(CutBatchOP.objects.filter(page__image=image_name),many=True)
            return Response(JSONRenderer().render(cut_datas.data))

        @list_route(methods=['get'], url_path='fetch_cut_64')
        def fetch_64(self, request):
            image_name = request.query_params['image']
            cut_datas = CutBatchOPSerializer(CutBatchOP.objects.filter(image=image_name), many=True)
            cut_64 = base64.b64encode(JSONRenderer().render(cut_datas.data))
            return Response(cut_64)'''
    '''@list_route(methods=['post'], url_path='up_result')
    def up_64(self,request):
        up_datas = json.loads(base64.b64decode(request.data))
        info_cut = ""
        for d in up_datas:
            op = d['op']
            add_flag = False
            if op == 0:
                if not add_flag:
                    info_cut = CutBatchOP.objects.get(pk=d['id'])
                pass
            elif op == 1:
                c = CutBatchOP.objects.get(pk=d['id'])
                c.x = d['x']
                c.y = d['y']
                c.width = d['width']
                c.height = d['height']
                c.op = 1
                #c.user = request.user
                # TODO 取消注释
            elif op == 2:
                c = CutBatchOP.objects.get(pk=d['id'])
                if c.op == 3:
                    c.delete()
                else:
                    c.op = 2
                    c.save()
                # TODO 新增后修改再删除如何处理？
            elif op == 3:
                c = CutBatchOP(
                        batch_version=info_cut.batch_version,
                        image=info_cut.image,
                        x=d['x'],
                        y=d['y'],
                        width=d['width'],
                        height=d['height'],
                        confidence=1,
                        op=3)
                # TODO 增加user
                c.save()
        #TODO 准备测试数据
        return Response({"status":"ok"})
    '''