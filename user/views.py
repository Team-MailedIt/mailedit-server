from django.http.response import Http404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, permissions
from django.contrib.auth import get_user_model, authenticate
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.google import views as google_view
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from .serializers import UserSerializer
import utils.email_verification as email_verification_helper
from django.utils.encoding import force_bytes, force_str
from utils.token_generator import account_activation_token
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
import requests
from project.settings.base import BASE_URL, CLIENT_ID, CLIENT_SECRET
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


# Create your views here.
GOOGLE_TOKEN_URI = "https://oauth2.googleapis.com/token"
GOOGLE_EMAIL_URI = "https://www.googleapis.com/oauth2/v1/tokeninfo"
REDIRECT_URI = BASE_URL + "/api/google/redirect"
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


class GoogleRedirectView(APIView):
    # 임시 View. 프런트에서 구현
    def get(self, request):
        code = request.query_params.get("code")
        return Response(
            {
                "code": code,
            },
            status=status.HTTP_200_OK,
        )


class GoogleLoginCallBackView(APIView):
    # code를 받아와서 access_token 반환
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        code = request.query_params.get("code")

        # 받은 code를 이용해서 access_token 받아오기
        token_body = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code",
        }
        try:
            token_res = requests.post(GOOGLE_TOKEN_URI, data=token_body)
            token_res_data = token_res.json()
            return Response(token_res_data, status=status.HTTP_200_OK)

        except:
            return Response(
                {"error_msg": "토큰 발급 실패"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class GoogleLoginView(SocialLoginView):
    adapter_class = google_view.GoogleOAuth2Adapter
    callback_url = REDIRECT_URI
    client_class = OAuth2Client


class TestAuthView(APIView):
    # 로그인 했을때만 가능한 요청
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        return Response("Success", status=status.HTTP_200_OK)
