# -*- encoding:utf8 -*-
from models import CutBatchOP,BatchVersion,Page
from rest_framework import serializers

class CutBatchOPSerializer(serializers.ModelSerializer):
    class Meta:
        model = CutBatchOP
        fields = ['id','page', 'cut_data']
        class Meta:
            depth = 1

class PageSerializer(serializers.ModelSerializer):
    c_page = serializers.StringRelatedField(many=True)
    class Meta:
        model = Page
        fields = ['id', 'image', 'c_page']


class BatchVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BatchVersion
        fields = ['id', 'des', 'organiztion', 'submit_date', 'accepted']