from typing import OrderedDict
from django.http.response import Http404
from rest_framework import permissions, serializers, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Template, BaseTemplate, Group
from .serializers import (
    TemplateSerializer,
    TemplateDetailSerializer,
    BaseTemplateSerializer,
    GroupSerializer,
    GroupDetailSerializer,
)

# Create your views here.
class MyTemplateListView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        # 요청한 사용자가 보유한 템플릿 목록
        user = request.user
        templates = Template.objects.filter(user_id=user.id)

        # group_id로 필터링
        f_groupId = request.query_params.get("groupId", None)
        if f_groupId is None:
            pass
        elif f_groupId == "0":  # 일반 그룹
            templates = templates.filter(group_id__isnull=True)
        else:
            templates = templates.filter(group_id=f_groupId)

        # 가나다순 정렬
        templates = templates.order_by("title")
        serializer = TemplateDetailSerializer(templates, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        # 새로운 템플릿 저장
        data = request.data
        user = request.user
        serializer = TemplateSerializer(data=data)
        group_ids = Group.objects.filter(user_id=user.id).values_list("id", flat=True)
        if data["groupId"] != None:
            match = int(data["groupId"]) in group_ids
            if match == False:
                return Response(
                    {
                        "detail": "Wrong group",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if serializer.is_valid():
            template = serializer.save(user=user)
            template.group_id = data["groupId"]
            template.save()
            return Response(
                {
                    "detail": "Successfully created Template",
                    **serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {
                    "detail": "Invalid Template data",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class BaseTemplateListView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        templates = BaseTemplate.objects.all()

        # category 필터링
        f_category = request.query_params.get("category", None)
        if f_category is not None:
            templates = templates.filter(category=f_category)

        # 가나다순 정렬
        templates = templates.order_by("title")
        serializer = BaseTemplateSerializer(templates, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TemplateDetailView(APIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_template(self, pk):
        try:  # 마이 템플릿에서 검색
            template = Template.objects.get(pk=pk)
            return (template, False)

        except Template.DoesNotExist:
            # 마이 템플릿에 해당 id의 템플릿이 없는 경우
            try:  # 기본 템플릿 중에서 검색
                template = BaseTemplate.objects.get(pk=pk)
                return (template, True)
            except BaseTemplate.DoesNotExist:  # 기본 템플릿 중에도 없으면
                raise Http404

    # 템플릿 조회
    def get(self, request, pk):
        template, isBase = self.get_template(pk)
        if isBase:
            serializer = BaseTemplateSerializer(template)
        else:
            serializer = TemplateDetailSerializer(template)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 템플릿 수정
    def patch(self, request, pk):
        try:
            template = Template.objects.get(pk=pk)
        except Template.DoesNotExist:
            raise Http404

        data = request.data
        user = request.user
        serializer = TemplateSerializer(template, data=data, partial=True)
        group_ids = Group.objects.filter(user_id=user.id).values_list("id", flat=True)
        if data["groupId"] != None:
            match = int(data["groupId"]) in group_ids
            if match == False:
                return Response(
                    {
                        "detail": "Wrong group",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if serializer.is_valid(raise_exception=True):
            template = serializer.save()
            template.group_id = data["groupId"]
            template.save()
            return Response(
                {
                    "detail": "Successfully updated template",
                    **serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {
                    "detail": "Invalid Request",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    def delete(self, request, pk):
        try:
            template = Template.objects.get(pk=pk)
        except Template.DoesNotExist:
            raise Http404
        template.delete()
        return Response(
            {"detail": "Successfully deleted Template"}, status=status.HTTP_200_OK
        )


class AllTemplateListView(APIView):
    permission_classes = (permissions.AllowAny,)

    # 마이템플릿 + 기본템플릿 리스트 조회
    def get(self, request):
        result = list()

        # 응답 결과에 기본템플릿 추가
        base_templates = BaseTemplate.objects.all()
        base_serializer = BaseTemplateSerializer(base_templates, many=True)
        result += base_serializer.data

        user = request.user
        # 응답 결과에 마이템플릿 추가. 로그인 했을 경우
        if user:
            my_templates = Template.objects.filter(user_id=user.id)
            my_serializer = TemplateSerializer(my_templates, many=True)
            result += my_serializer.data

        # 가나다 순으로 정렬
        result.sort(key=lambda template: template["title"])

        return Response(
            result,
            status=status.HTTP_200_OK,
        )


class GroupListView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    # 그룹 리스트 조회
    def get(self, request):
        user = request.user
        result = list()

        # 기본으로 존재하는 일반그룹. id=0
        result += [
            {"userId": request.user.id, "id": 0, "name": "일반", "color": "#CED4DA"}
        ]
        groups = Group.objects.filter(user_id=user.id)
        serializer = GroupSerializer(groups, many=True)
        result += serializer.data
        return Response(result, status=status.HTTP_200_OK)

    # 그룹 생성
    def post(self, request):
        data = request.data
        user = request.user
        serializer = GroupSerializer(data=data, context={"request": request})
        if serializer.is_valid():
            group = serializer.save(user=user)
            return Response(
                {
                    "detail": "Successfully created Group",
                    **serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {
                    "detail": "Invalid data",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class GroupDetailView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    # 그룹 상세 조회
    def get(self, request, id):
        try:
            group = Group.objects.get(pk=id)
        except Group.DoesNotExist:
            raise Http404
        serializer = GroupDetailSerializer(group, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 그룹 편집
    def patch(self, request, id):
        try:
            group = Group.objects.get(pk=id)
        except Group.DoesNotExist:
            raise Http404
        data = request.data
        serializer = GroupSerializer(
            group, data=data, context={"request": request}, partial=True
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {
                    "detail": "Successfully updated group",
                    **serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {
                    "detail": "Invalid Request",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    # 그룹 삭제
    def delete(self, request, id):
        try:
            group = Group.objects.get(pk=id)
        except Group.DoesNotExist:
            raise Http404
        group.delete()
        return Response(
            {"detail": "Successfully deleted group"}, status=status.HTTP_200_OK
        )
