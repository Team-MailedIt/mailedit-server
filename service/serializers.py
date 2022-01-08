from rest_framework import serializers
from .models import Template, BaseTemplate, Group


class TemplateSerializer(serializers.ModelSerializer):
    userId = serializers.SerializerMethodField()
    templateId = serializers.SerializerMethodField()
    createdAt = serializers.SerializerMethodField()
    updatedAt = serializers.SerializerMethodField()

    class Meta:
        model = Template
        fields = (
            "userId",
            "templateId",
            "title",
            "subtitle",
            "isStar",
            "content",
            "createdAt",
            "updatedAt",
        )

    def get_templateId(self, obj):
        return obj.id

    def get_userId(self, obj):
        return obj.user_id

    def get_createdAt(self, obj):
        return obj.created_at

    def get_updatedAt(self, obj):
        return obj.updated_at


class BaseTemplateSerializer(serializers.ModelSerializer):
    templateId = serializers.SerializerMethodField()

    class Meta:
        model = BaseTemplate
        fields = ("templateId", "title", "subtitle", "content")

    def get_templateId(self, obj):
        return obj.id


class GroupSerializer(serializers.ModelSerializer):
    userId = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ("userId", "id", "name", "color")

    def get_userId(self, obj):
        return obj.user_id

    def validate(self, data):
        user = self.context.get("request").user
        groups = Group.objects.filter(user_id=user.id)

        for group in groups:
            if group.color == data["color"]:
                raise serializers.ValidationError("Color must be different")
        return data
