from rest_framework import viewsets

from api.serializers import RectSerializer
from core.models import Rect, Page
from rest_framework import filters
from rest_framework.permissions import AllowAny

from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework import status
from lib.utils import retrieve_rects, page_id


class RectViewSet(viewsets.ModelViewSet):
    serializer_class = RectSerializer
    queryset = Rect.objects.all()
    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter)
    ordering_fields = ('confidence', 'page')
    ordering = ('confidence',)
    permission_classes = (AllowAny,)
    filter_fields = ('line_no',)

    @detail_route(methods=["get"], url_path="split")
    def get_rect_split(self, request, pk):
        pk = pk
        rect = Rect.objects.get(pk=pk)
        line_no, col_no, page = rect.line_no, rect.col_no, rect.page
        rects = Rect.objects.filter(page=rect.page, line_no=line_no).all()
        # {"id":"","code":"","image_url":"","json_data":""}

        return Response(
            {
                "id": pk,
                "x": rect.x,
                "width": rect.width,
                "page_id": rect.page_id,
                "line_no": line_no,
                "col_no": col_no,
                "image_url": page.get_image_url,
                "rects": list(dict(qs) for qs in rects)
            })

    @detail_route(methods=['get'], url_path='list')
    def rectlist(self, request, pk):
        user = request.user
        queryset, image_url = retrieve_rects(user)
        serializer = RectSerializer(queryset, many=True)
        return Response({
            "models": serializer.data,
            "image_url": image_url,
            "page_id": page_id(user.id)
        })

    @detail_route(methods=['post'], url_path='done')
    def confidence_done(self, request, pk):
        page = Page.objects.get(pk=pk)
        page.locked = 2
        page.save()
        return Response({
            "page_id": pk
        })

    def create(self, request):
        page_id = request.data['page_id']
        serializer = RectSerializer(data=request.data)
        if serializer.is_valid():
            page = Page.objects.get(pk=page_id)
            rect = serializer.save()
            rect.page = page
            rect.save()
            page.reformat_rects()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def put(self, request, pk, format=None):
        rect = self.get_object(pk)
        serializer = RectSerializer(rect, data=request.data)
        if serializer.is_valid():
            serializer.save()
            rect.page.reformat_rects()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        rect = self.get_object(pk)
        rect.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
