# -*- coding: utf-8 -*-

from rest_framework import serializers
from .models import Staff
from django.utils import timezone
import jwt
import pytz

from calendar import timegm
from datetime import datetime, timedelta
from django.contrib.auth import authenticate
from django.utils.translation import ugettext as _
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

from django.contrib.auth.backends import ModelBackend

class PasswordField(serializers.CharField):

    def __init__(self, *args, **kwargs):
        if 'style' not in kwargs:
            kwargs['style'] = {'input_type': 'password'}
        else:
            kwargs['style']['input_type'] = 'password'
        super(PasswordField, self).__init__(*args, **kwargs)


def get_username_field():
    return 'email'


jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
jwt_get_username_from_payload = api_settings.JWT_PAYLOAD_GET_USERNAME_HANDLER


def jwt_response_payload_handler(token, staff=None, request=None):
    staff.last_login = timezone.localtime(timezone.now())

#    import pdb;pdb.set_trace()
    staff.save(update_fields=['last_login'])

    return {
        'token': token,
        'staff': StaffSerializer(staff, context={'request': request}).data
    }

class StaffSerializer(serializers.ModelSerializer):

    # date_joined = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S",
    #     default_timezone=pytz.UTC, read_only=True)
    last_login = serializers.DateTimeField(format=_("%Y-%m-%d %H:%M:%S"),
        default_timezone=pytz.timezone('Asia/Shanghai'), read_only=True)

    class Meta:
        model = Staff
        fields = ('email', 'last_login', 'is_active', 'password')
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = ('created_at', 'updated_at', 'is_admin', 'last_login')

    def create(self, validated_data):
        staff = Staff(email=validated_data['email'])
        staff.set_password(validated_data['password'])
        staff.save()
        return staff



class JSONWebTokenSerializer(serializers.Serializer):
    """
    Serializer class used to validate a username and password.
    'username' is identified by the custom UserModel.USERNAME_FIELD.
    Returns a JSON Web Token that can be used to authenticate later calls.
    """
    def __init__(self, *args, **kwargs):
        """
        Dynamically add the USERNAME_FIELD to self.fields.
        """
        super(JSONWebTokenSerializer, self).__init__(*args, **kwargs)

        self.fields[self.username_field] = serializers.CharField()
        self.fields['password'] = PasswordField(write_only=True)

    @property
    def object(self):
        return self.validated_data

    @property
    def username_field(self):
        return get_username_field()

    def authenticate(self, username=None, password=None, **kwargs):
        try:
            user = Staff.objects.get(email=username)
            if user.check_password(password):
                return user
        except Exception as e:
            return None

    def validate(self, attrs):
        credentials = {
            self.username_field: attrs.get(self.username_field),
            'password': attrs.get('password')
        }

        if all(credentials.values()):
            user = self.authenticate(attrs.get(self.username_field), attrs.get('password'))

            if user:
                if not user.is_active:
                    msg = _('User account is disabled.')
                    raise serializers.ValidationError(msg)

                payload = jwt_payload_handler(user)

                return {
                    'token': jwt_encode_handler(payload),
                    'user': user
                }
            else:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg)
        else:
            msg = _('Must include "{username_field}" and "password".')
            msg = msg.format(username_field=self.username_field)
            raise serializers.ValidationError(msg)



class VerificationBaseSerializer(serializers.Serializer):
    """
    Abstract serializer used for verifying and refreshing JWTs.
    """
    token = serializers.CharField()

    def validate(self, attrs):
        msg = 'Please define a validate method.'
        raise NotImplementedError(msg)

    def _check_payload(self, token):
        # Check payload valid (based off of JSONWebTokenAuthentication,
        # may want to refactor)
        try:
            payload = jwt_decode_handler(token)
        except jwt.ExpiredSignature:
            msg = _('Signature has expired.')
            raise serializers.ValidationError(msg)
        except jwt.DecodeError:
            msg = _('Error decoding signature.')
            raise serializers.ValidationError(msg)

        return payload

    def _check_user(self, payload):
        username = jwt_get_username_from_payload(payload)

        if not username:
            msg = _('Invalid payload.')
            raise serializers.ValidationError(msg)

        # Make sure user exists
        try:
            user = Staff.objects.get_by_natural_key(username)
        except Staff.DoesNotExist:
            msg = _("User doesn't exist.")
            raise serializers.ValidationError(msg)

        if not user.is_active:
            msg = _('User account is disabled.')
            raise serializers.ValidationError(msg)

        return user

class RefreshJSONWebTokenSerializer(VerificationBaseSerializer):
    """
    Refresh an access token.
    """
    @property
    def object(self):
        return self.validated_data

    def validate(self, attrs):

        token = attrs['token']

        payload = self._check_payload(token=token)
        user = self._check_user(payload=payload)

        if api_settings.JWT_ALLOW_REFRESH:
            payload['orig_iat'] = timegm(
                datetime.utcnow().utctimetuple()
            )

        # Get and check 'orig_iat'
        orig_iat = payload.get('orig_iat')

        if orig_iat:
            # Verify expiration
            refresh_limit = api_settings.JWT_REFRESH_EXPIRATION_DELTA

            if isinstance(refresh_limit, timedelta):
                refresh_limit = (refresh_limit.days * 24 * 3600 +
                                 refresh_limit.seconds)

            expiration_timestamp = orig_iat + int(refresh_limit)
            now_timestamp = timegm(datetime.utcnow().utctimetuple())

            if now_timestamp > expiration_timestamp:
                msg = _('Refresh has expired.')
                raise serializers.ValidationError(msg)
        else:
            msg = _('orig_iat field is required.')
            raise serializers.ValidationError(msg)

        new_payload = jwt_payload_handler(user)
        new_payload['orig_iat'] = orig_iat

        return {
            'token': jwt_encode_handler(new_payload),
            'user': user
        }
