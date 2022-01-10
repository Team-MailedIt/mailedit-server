from rest_framework import serializers
from utils.service.group_validation_service import (
    group_name_validator,
    group_color_validator,
    color_hex_validator,
)
from .models import Template, BaseTemplate, Group


class GroupSerializer(serializers.ModelSerializer):
    userId = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ("userId", "id", "name", "color")

    def get_userId(self, obj):
        return obj.user_id

    def validate(self, data):
        user = self.context.get("request").user
        group_name_validator(data["name"], user)
        group_color_validator(data["color"], user)
        color_hex_validator(data["color"])
        return data


class TemplateSerializer(serializers.ModelSerializer):
    userId = serializers.SerializerMethodField()
    templateId = serializers.SerializerMethodField()
    createdAt = serializers.SerializerMethodField()
    updatedAt = serializers.SerializerMethodField()
    groupId = serializers.SerializerMethodField()

    class Meta:
        model = Template
        fields = (
            "userId",
            "templateId",
            "title",
            "subtitle",
            "isStar",
            "groupId",
            "content",
            "createdAt",
            "updatedAt",
        )

    def get_templateId(self, obj):
        return obj.id

    def get_userId(self, obj):
        return obj.user_id

    def get_groupId(self, obj):
        return obj.group_id

    def get_createdAt(self, obj):
        return obj.created_at

    def get_updatedAt(self, obj):
        return obj.updated_at


class TemplateDetailSerializer(TemplateSerializer):
    group = GroupSerializer(many=False, read_only=True)

    class Meta:
        model = Template
        fields = (
            "userId",
            "templateId",
            "title",
            "subtitle",
            "isStar",
            "groupId",
            "group",
            "content",
            "createdAt",
            "updatedAt",
        )


class BaseTemplateSerializer(serializers.ModelSerializer):
    templateId = serializers.SerializerMethodField()

    class Meta:
        model = BaseTemplate
        fields = ("templateId", "title", "subtitle", "category", "content")

    def get_templateId(self, obj):
        return obj.id


class GroupDetailSerializer(GroupSerializer):
    group_templates = TemplateSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = ("userId", "id", "name", "color", "group_templates")
