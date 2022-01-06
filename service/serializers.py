from rest_framework import serializers
from .models import Template, BaseTemplate


class TemplateSerializer(serializers.ModelSerializer):
    userId = serializers.SerializerMethodField()
    templateId = serializers.SerializerMethodField()

    class Meta:
        model = Template
        fields = (
            "userId",
            "templateId",
            "sub_id",
            "title",
            "subtitle",
            "isStar",
            "content",
        )

    def get_templateId(self, obj):
        return obj.id

    def get_userId(self, obj):
        return obj.user_id


class BaseTemplateSerializer(serializers.ModelSerializer):
    templateId = serializers.SerializerMethodField()

    class Meta:
        model = BaseTemplate
        fields = ("templateId", "sub_id", "title", "subtitle", "content")

    def get_templateId(self, obj):
        return obj.id
