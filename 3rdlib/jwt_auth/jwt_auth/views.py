from rest_framework import viewsets, permissions, mixins, generics
from .models import Staff
from .serializers import StaffSerializer, JSONWebTokenSerializer, RefreshJSONWebTokenSerializer
from rest_framework_jwt.views import JSONWebTokenAPIView


class CreateStaffView(mixins.CreateModelMixin, generics.GenericAPIView):
    queryset = Staff.objects.all()
    permission_classes = (permissions.AllowAny, )
    serializer_class = StaffSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class StaffViewSet(viewsets.ModelViewSet):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = (permissions.IsAuthenticated, )


class ObtainJSONWebToken(JSONWebTokenAPIView):
    """
    API View that receives a POST with a user's username and password.
    Returns a JSON Web Token that can be used for authenticated requests.
    """
    serializer_class = JSONWebTokenSerializer


class RefreshJSONWebToken(JSONWebTokenAPIView):
    """
    API View that returns a refreshed token (with new expiration) based on
    existing token
    If 'orig_iat' field (original issued-at-time) is found, will first check
    if it's within expiration window, then copy it to the new token
    """
    serializer_class = RefreshJSONWebTokenSerializer


register_user = CreateStaffView.as_view()
obtain_jwt_token = ObtainJSONWebToken.as_view()
refresh_jwt_token = RefreshJSONWebToken.as_view()





