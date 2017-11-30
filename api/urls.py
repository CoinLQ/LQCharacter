from rest_framework import routers
from .views.page_views import CutBatchOPViewSet, BatchVersionViewSet, PageViewSet
from .views.rect_views import RectViewSet
from .views.split_task_views import SplitTaskViewSet
from django.conf.urls import url, include
from rest_framework.schemas import get_schema_view
from rest_framework_swagger.renderers import OpenAPIRenderer, SwaggerUIRenderer

router = routers.SimpleRouter(trailing_slash=False)
router.register(r'cutbatch', CutBatchOPViewSet)
router.register(r'batchversion', BatchVersionViewSet)
router.register(r'pages', PageViewSet)
router.register(r'rects', RectViewSet)
router.register(r'split_tasks', SplitTaskViewSet)

schema_view = get_schema_view(
    title='Example API',
    renderer_classes=[OpenAPIRenderer, SwaggerUIRenderer]
)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^swagger/$', schema_view),

]
