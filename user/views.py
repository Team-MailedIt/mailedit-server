from user.services import google_user_get_or_create, google_validate_id_token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, permissions
from django.contrib.auth import get_user_model, authenticate
from .serializers import UserSerializer
import utils.email_verification as email_verification_helper
from django.utils.encoding import force_bytes, force_str
from utils.token_generator import account_activation_token
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
import requests
from project.settings.base import BASE_URL, CLIENT_ID, CLIENT_SECRET
from dj_rest_auth.utils import jwt_encode

# Create your views here.
GOOGLE_VALIDATE_TOKEN_URI = "https://www.googleapis.com/oauth2/v3/tokeninfo"
GOOGLE_ACCESS_TOKEN_URI = "https://oauth2.googleapis.com/token"
User = get_user_model()


# 회원가입
class EmailRegisterAPIView(APIView):
    def post(self, request):
        user_serializer = UserSerializer(data=request.data)
        if user_serializer.is_valid():
            try:
                user = user_serializer.save()
            except:
                return Response(
                    user_serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )

            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)

            email_verification_helper.send_verification_link(
                user.email,
                verification_link=f"http://127.0.0.1:8000/activate/{uidb64}/{token}",
            )
            return Response(
                {"message": "email verification link sent"}, status=status.HTTP_200_OK
            )
        return Response(
            {"message": "sign up failed"}, status=status.HTTP_400_BAD_REQUEST
        )


class ActivateUserAPIView(APIView):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)

            if account_activation_token.check_token(user, token):
                user.is_active = True
                user.save()
                user_serializer = UserSerializer(user)
                return Response(user_serializer.data, status=status.HTTP_200_OK)

            return Response(
                {"message": "AUTH FAIL"}, status=status.HTTP_400_BAD_REQUEST
            )

        except ValidationError:
            return Response(
                {"message": "TYPE_ERROR"}, status=status.HTTP_400_BAD_REQUEST
            )
        except KeyError:
            return Response(
                {"message": "INVALID_KEY"}, status=status.HTTP_400_BAD_REQUEST
            )


class TestAuthView(APIView):
    # 로그인 했을때만 가능한 요청
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        return Response("Success", status=status.HTTP_200_OK)


class GoogleLoginAPIView(APIView):
    permission_classes = (permissions.AllowAny,)

    # 클라이언트에서 idToken 받아와서 로그인/회원가입 실행
    def get(self, request, *args, **kwargs):
        id_token = request.query_params.get("idToken")
        user_data = google_validate_id_token(id_token=id_token)

        profile_data = {
            "email": user_data["email"],
            "username": user_data.get("given_name", ""),
            "login_type": "GOOGLE",
        }

        # We use get-or-create logic here for the sake of the example.
        # We don't have a sign-up flow.
        user, _ = google_user_get_or_create(**profile_data)
        access_token, refresh_token = jwt_encode(user)
        print(f"access_token: {access_token} refresh_token: {refresh_token}")
        return Response(
            {
                "access_token": str(access_token),
                "refresh_token": str(refresh_token),
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )