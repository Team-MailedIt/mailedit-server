from rest_framework import serializers
from utils.service.group_validation_service import (
    group_name_validator,
    group_color_validator,
    color_hex_validator,
)
from .models import Template, BaseTemplate, Group
from utils.service.general_group_info import GENERAL_GROUP_INFO


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

    def create(self, validated_data):
        if validated_data.get("subtitle", "") == "":
            generated_subtitle = (validated_data["content"][0])["html"]
            validated_data["subtitle"] = generated_subtitle
        return super().create(validated_data)

    def get_templateId(self, obj):
        return obj.id

    def get_userId(self, obj):
        return obj.user_id

    def get_groupId(self, obj):
        if obj.group_id == None:  # 그룹이 지정되지 않음 (일반 그룹)
            return 0
        return obj.group_id

    def get_createdAt(self, obj):
        return obj.created_at

    def get_updatedAt(self, obj):
        return obj.updated_at


class TemplateDetailSerializer(TemplateSerializer):
    # group = GroupSerializer(many=False, read_only=True)
    group = serializers.SerializerMethodField()

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

    def get_group(self, obj):
        if obj.group_id == None:  # 일반 그룹인 경우
            return {"userId": obj.user_id, **GENERAL_GROUP_INFO}
        else:
            group = Group.objects.get(id=obj.group_id)
            serializer = GroupSerializer(group)
            return serializer.data


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
