from core.models import CutBatchOP, BatchVersion, Page, OPage, Rect
from rest_framework import serializers


class CutBatchOPSerializer(serializers.ModelSerializer):
    class Meta:
        model = CutBatchOP
        fields = ['id', 'page', 'cut_data']

        class Meta:
            depth = 1


class PageSerializer(serializers.ModelSerializer):
    c_page = serializers.StringRelatedField(many=True)

    class Meta:
        model = Page
        fields = ['id', 'batch_version', 'image_name', 'image_md5', 'c_page']


class BatchVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BatchVersion
        fields = ['id', 'des', 'organiztion', 'submit_date', 'accepted']


class OPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = OPage
        fields = ['id', 'name', 'final', 'md5']


class RectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rect
        fields = ['id', 'line_no', 'col_no', 'x', 'y', 'width', 'height', 'confidence',
                  'op', 'hans', 'inset_uri', 'page_id']


class SplitRectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rect
        fields = ['id', 'line_no', 'col_no', 'x', 'y', 'width', 'height', 'confidence',
                  'op', 'hans', 'inset_datauri', 'page_id']