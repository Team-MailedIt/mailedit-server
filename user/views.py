from utils.user.google_auth_service import (
    google_user_get_or_create,
    google_validate_id_token,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, permissions
from django.contrib.auth import get_user_model, authenticate
from .serializers import UserSerializer
import utils.user.email_verification_service as email_verification_helper
from django.utils.encoding import force_bytes, force_str
from utils.user.token_generation_service import account_activation_token
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from project.settings.base import BASE_URL
from dj_rest_auth.utils import jwt_encode

# Create your views here.
User = get_user_model()


# 회원가입
class EmailRegisterAPIView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        user_serializer = UserSerializer(data=request.data)
        if user_serializer.is_valid():
            try:
                user = user_serializer.save()
                user.is_active = False
                user.save()
            except:
                return Response(
                    user_serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )

            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)

            email_verification_helper.send_verification_link(
                user.email,
                verification_link=f"{BASE_URL}/activate/{uidb64}/{token}",
            )
            return Response(
                {"detail": "email verification link sent"}, status=status.HTTP_200_OK
            )
        return Response(
            {"detail": "sign up failed"}, status=status.HTTP_400_BAD_REQUEST
        )


class ActivateUserAPIView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)

            if account_activation_token.check_token(user, token):
                user.is_active = True
                user.save()
                return redirect(email_verified)

            return Response({"detail": "AUTH FAIL"}, status=status.HTTP_400_BAD_REQUEST)

        except ValidationError:
            return Response(
                {"detail": "TYPE_ERROR"}, status=status.HTTP_400_BAD_REQUEST
            )
        except KeyError:
            return Response(
                {"detail": "INVALID_KEY"}, status=status.HTTP_400_BAD_REQUEST
            )


# 일반 이메일 인증 메일 재발급
class RetryVerificationAPI(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        user = User.objects.get(email=request.data.get("email"))
        if user is not None and user.is_active is False:
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)

            email_verification_helper.send_verification_link(
                user.email, verification_link=f"{BASE_URL}/activate/{uidb64}/{token}"
            )

            return Response(
                {"detail": "email verification link sent"}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"detail": "user not found"}, status=status.HTTP_400_BAD_REQUEST
            )


# 일반 이메일 로그인
class EmailLoginAPIView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        user = authenticate(
            username=request.data.get("email"), password=request.data.get("password")
        )
        if user is not None and user.is_active is True:
            access_token, refresh_token = jwt_encode(user)
            print(refresh_token)
            res = Response(
                {
                    "user": {
                        "username": user.username,
                    },
                    "detail": "Successfully logged in",
                    "token": {
                        "refresh": str(refresh_token),
                        "access": str(access_token),
                    },
                },
                status=status.HTTP_200_OK,
            )
            return res
        else:
            return Response(
                {"detail": "Invalid User"}, status=status.HTTP_400_BAD_REQUEST
            )


class TestAuthView(APIView):
    # 로그인 했을때만 가능한 요청
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        return Response("Success", status=status.HTTP_200_OK)


class GoogleLoginAPIView(APIView):
    permission_classes = (permissions.AllowAny,)

    # 클라이언트에서 idToken 받아와서 로그인/회원가입 실행
    def post(self, request, *args, **kwargs):
        id_token = request.data.get("idToken")
        user_data = google_validate_id_token(id_token=id_token)

        profile_data = {
            "email": user_data["email"],
            "username": user_data.get("given_name", ""),
            "login_type": "GOOGLE",
        }

        # We use get-or-create logic here for the sake of the example.
        # We don't have a sign-up flow.
        user, isNew = google_user_get_or_create(**profile_data)
        if not user:
            return Response(
                {"detail": "해당 이메일로 가입한 일반 사용자가 존재합니다."},
                status=status.status.HTTP_400_BAD_REQUEST,
            )

        access_token, refresh_token = jwt_encode(user)
        if isNew:  # 회원가입 성공
            return Response(
                {
                    "user": UserSerializer(user).data,
                    "detail": "Successfully signed up",
                    "token": {
                        "access": str(access_token),
                        "refresh": str(refresh_token),
                    },
                },
                status=status.HTTP_200_OK,
            )
        else:  # 로그인 성공
            return Response(
                {
                    "user": UserSerializer(user).data,
                    "detail": "Successfully logged in",
                    "token": {
                        "access": str(access_token),
                        "refresh": str(refresh_token),
                    },
                },
                status=status.HTTP_200_OK,
            )


def email_verified(request):
    return render(request, "user/email_verified.html")
