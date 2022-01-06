from django.http import request
from django.http.response import Http404
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Template, BaseTemplate
from .serializers import TemplateSerializer, BaseTemplateSerializer

# Create your views here.
class MyTemplateListView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        # 요청한 사용자가 보유한 템플릿 목록
        user = request.user
        templates = Template.objects.filter(user_id=user.id)
        serializer = TemplateSerializer(templates, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BaseTemplateListView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        templates = BaseTemplate.objects.all()
        serializer = BaseTemplateSerializer(templates, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TemplateDetailView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get_template(self, sub_id):
        try:  # 마이 템플릿에서 검색
            template = Template.objects.get(sub_id=sub_id)
            return (template, False)

        except Template.DoesNotExist:
            # 마이 템플릿에 해당 id의 템플릿이 없는 경우
            try:  # 기본 템플릿 중에서 검색
                template = BaseTemplate.objects.get(sub_id=sub_id)
                return (template, True)
            except BaseTemplate.DoesNotExist:  # 기본 템플릿 중에도 없으면
                raise Http404

    def get(self, request, sub_id):
        template, isBase = self.get_template(sub_id)
        if isBase:
            serializer = BaseTemplateSerializer(template)
        else:
            serializer = TemplateSerializer(template)
        return Response(serializer.data, status=status.HTTP_200_OK)
