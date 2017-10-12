from rest_framework import viewsets

from api.serializers import RectSerializer
from core.models import Rect
from rest_framework import filters
from rest_framework.permissions import AllowAny


class RectViewSet(viewsets.ModelViewSet):
    serializer_class = RectSerializer
    queryset = Rect.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    permission_classes = (AllowAny,)
    filter_fields = ('line_no',)
