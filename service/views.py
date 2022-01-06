from django.http.response import Http404
from rest_framework import permissions, serializers, status
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
        print(user)
        templates = Template.objects.filter(user_id=user.id)
        serializer = TemplateSerializer(templates, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        # 새로운 템플릿 저장
        data = request.data
        user = request.user
        serializer = TemplateSerializer(data=data)
        if serializer.is_valid():
            template = serializer.save(user=user)
            return Response(
                {
                    "message": "Successfully created Template",
                    **serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {
                    "message": "Invalid Template data",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class BaseTemplateListView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        templates = BaseTemplate.objects.all()
        serializer = BaseTemplateSerializer(templates, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TemplateDetailView(APIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

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

    # 템플릿 조회
    def get(self, request, sub_id):
        template, isBase = self.get_template(sub_id)
        if isBase:
            serializer = BaseTemplateSerializer(template)
        else:
            serializer = TemplateSerializer(template)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 템플릿 수정
    def put(self, request, sub_id):
        try:
            template = Template.objects.get(sub_id=sub_id)
        except Template.DoesNotExist:
            raise Http404
        data = request.data
        serializer = TemplateSerializer(template, data=data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {
                    "message": "Successfully updated template",
                    **serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {
                    "message": "Invalid Request",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    def delete(self, request, sub_id):
        try:
            template = Template.objects.get(sub_id=sub_id)
        except Template.DoesNotExist:
            raise Http404
        template.delete()
        return Response(
            {"message": "Successfully deleted Template"}, status=status.HTTP_200_OK
        )
