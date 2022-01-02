from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model, authenticate
from .serializers import UserSerializer
import requests
from project.settings.base import CLIENT_ID, CLIENT_SECRET

# Create your views here.
GOOGLE_TOKEN_URI = "https://oauth2.googleapis.com/token"
REDIRECT_URI = "http://localhost:8000/api/google/callback"


class SignUpAPIView(APIView):
    def post(self, request):
        user_serializer = UserSerializer(data=request.data)
        if user_serializer.is_valid():
            # 사용자 생성
            user = user_serializer.save()
            return Response({"user": user_serializer.data}, status=status.HTTP_200_OK)
        else:
            # 사용자 생성 실패
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GoogleLoginCallBackView(APIView):
    def get(self, request):
        print(dict(request.GET))
        code = request.query_params.get("code")
        redirect_uri = "http://localhost:8000/api/google/callback"
        # body = {
        #     "client_id": CLIENT_ID,
        #     "client_secret": CLIENT_SECRET,
        #     "code": code,
        #     "redirect_uri": redirect_uri,
        #     "grant_type": "authorization_code",
        # }
        body = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": "1//0eSKTdO4_K4s8CgYIARAAGA4SNwF-L9IrMcD6Nontr_p-clIOp526se4V2dhakyKsGX6-f8hpKLhNkCbZj1OF1IjJOupgNAmRh7Q",
            "grant_type": "refresh_token",
        }
        try:
            res = requests.post("https://oauth2.googleapis.com/token", data=body)
            print(res.json())
        except:
            print(res.status_code)
        return Response(status=status.HTTP_200_OK)


class TestAPIView(APIView):
    def get(self, request):
        body = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": "1//0eSKTdO4_K4s8CgYIARAAGA4SNwF-L9IrMcD6Nontr_p-clIOp526se4V2dhakyKsGX6-f8hpKLhNkCbZj1OF1IjJOupgNAmRh7Q",
            "grant_type": "refresh_token",
        }
        res = requests.post("https://oauth2.googleapis.com/token", data=body)
        print(res.json())
        return Response(status=status.HTTP_200_OK)