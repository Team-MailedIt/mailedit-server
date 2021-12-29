from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model, authenticate
from .serializers import UserSerializer

# Create your views here.


class SignUpAPIView(APIView):
    def post(self, request):
        user_serializer = UserSerializer(data=request.data)
        if user_serializer.is_valid():
            # 사용자 생성
            user = user_serializer.save()
            return Response({
                'user': user_serializer.data
            }, status=status.HTTP_200_OK)
        else:
            # 사용자 생성 실패
            return Response(
                user_serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
