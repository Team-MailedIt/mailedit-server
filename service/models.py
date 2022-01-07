from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.deletion import CASCADE
from django_extensions.validators import HexValidator
import uuid

# Create your models here.
User = get_user_model()


class TimeStampedModel(models.Model):
    # 최초 생성 일자
    created_at = models.DateTimeField(auto_now_add=True)
    # 최종 수정 일자
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Template(TimeStampedModel):  # 템플릿
    sub_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    # 제목과 부제목
    title = models.CharField(max_length=50, blank=False, null=False)
    subtitle = models.CharField(max_length=30, blank=True, null=False)

    # 즐겨찾기 여부
    isStar = models.BooleanField(default=False)

    # 템플릿 내용. json 배열로 이루어짐
    content = models.JSONField(default=list)

    # 템플릿 소유한 사용자
    user = models.ForeignKey(User, on_delete=CASCADE, related_name="user_templates")

    REQUIRED_FIELDS = [
        "title",
        "content",
    ]

    def __str__(self):
        return self.title


class BaseTemplate(models.Model):
    sub_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=50, blank=False, null=False)
    subtitle = models.CharField(max_length=30, blank=True, null=False)
    content = models.JSONField(default=list)

    def __str__(self):
        return self.title


class Block(TimeStampedModel):
    # 고유 id
    id = models.CharField(max_length=30, primary_key=True, unique=True)
    # 각 템플릿에서 몇번째 순서인지
    index = models.IntegerField()
    # 블록 내 텍스트
    text = models.TextField()
    # html tag
    tag = models.CharField(max_length=10)
    # 블록 여부
    flag = models.BooleanField(default=False)
    # 블록이 속한 템플릿
    template = models.ForeignKey(
        Template, on_delete=CASCADE, related_name="template_blocks", null=True
    )


class Group(TimeStampedModel):
    # 그룹 이름
    name = models.CharField(max_length=20, blank=False, null=False)
    # 구별 색의 hex값
    color = models.CharField(max_length=6, validators=[HexValidator(length=6)])
    # 그룹 소유 사용자
    user = models.ForeignKey(User, on_delete=CASCADE, related_name="user_groups")
