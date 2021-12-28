from django.db import models

# Create your models here.


class TimeStampedModel(models.Model):
    # 최초 생성 일자
    created_at = models.DateTimeField(auto_now_add=True)
    # 최종 수정 일자
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Template(TimeStampedModel):
    # 템플릿

    # 제목과 부제목
    title = models.CharField(max_length=50, blank=False, null=False)
    subtitle = models.CharField(max_length=30, blank=True, null=False)

    # 기본 템플릿 여부
    isBase = models.BooleanField(default=False)
    isStar = models.BooleanField(default=False)

    # 템플릿 내용. json 배열로 이루어짐
    content = models.JSONField(default=[])


class Block(TimeStampedModel):
    # 각 템플릿에서 몇번째 순서인지
    index = models.IntegerField()
    # 블록 내 텍스트
    text = models.TextField()
    # html tag
    tag = models.CharField(max_length=10)
    # 블록 여부
    flag = models.BooleanField(default=False)
