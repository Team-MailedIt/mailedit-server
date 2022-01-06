from rest_framework import serializers
from .models import Template, BaseTemplate


class TemplateSerializer(serializers.ModelSerializer):
    userId = serializers.SerializerMethodField()

    class Meta:
        model = Template
        fields = ("userId", "id", "sub_id", "title", "subtitle", "isStar", "content")

    def get_userId(self, obj):
        return obj.user_id


class BaseTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseTemplate
        fields = ("id", "sub_id", "title", "subtitle", "content")
