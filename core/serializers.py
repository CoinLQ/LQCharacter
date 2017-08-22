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
    class Meta:
        model = Page
        fields = ['id', 'image']


class BatchVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BatchVersion
        fields = ['id', 'des', 'organiztion', 'submit_date', 'accepted']