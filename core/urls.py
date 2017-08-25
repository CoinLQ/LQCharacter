from rest_framework import routers
from .views import CutBatchOPViewSet, BatchVersionViewSet, PageViewSet
from django.conf.urls import url, include
from rest_framework.schemas import get_schema_view
from rest_framework_swagger.renderers import OpenAPIRenderer, SwaggerUIRenderer

router = routers.SimpleRouter(trailing_slash=False)
router.register(r'cutbatch', CutBatchOPViewSet)
router.register(r'batchversion', BatchVersionViewSet)
router.register(r'page', PageViewSet)


schema_view = get_schema_view(
    title='Example API',
    renderer_classes=[OpenAPIRenderer, SwaggerUIRenderer]
)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^swagger/$', schema_view)
]