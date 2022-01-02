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
GOOGLE_LOGIN_URI = BASE_URL + '/api/google/login'
REDIRECT_URI = BASE_URL + "/api/google/callback"
User = get_user_model()


# 일반 이메일 회원가입
class EmailRegisterAPIView(APIView):
    permission_classes = ( permissions.AllowAny, )

    def post(self, request):
        user_serializer = UserSerializer(data=request.data)
        if user_serializer.is_valid():
            try:
                user = user_serializer.save()
            except:
                return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)

            email_verification_helper.send_verification_link(
                user.email,
                verification_link=f"{BASE_URL}/activate/{uidb64}/{token}"
            )
            return Response({"message": "email verification link sent"}, status=status.HTTP_200_OK)
        return Response({"message": "sign up failed"}, status=status.HTTP_400_BAD_REQUEST)


class ActivateUserAPIView(APIView):
    permission_classes = ( permissions.AllowAny, )

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)

            if account_activation_token.check_token(user, token):
                user.is_active = True
                user.save()

                return Response({"message": "your email has been successfully verified"}, status=status.HTTP_200_OK)

            return Response({"message": "AUTH FAIL - please re-generate the verification link"}, status=status.HTTP_400_BAD_REQUEST)

        except ValidationError:
            return Response({"message": "TYPE_ERROR"}, status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            return Response({"message": "INVALID_KEY"}, status=status.HTTP_400_BAD_REQUEST)


# 일반 이메일 인증 메일 재발급
class RetryVerificationAPI(APIView):
    permission_classes = ( permissions.AllowAny, )

    def post(self, request):
        user = authenticate(
            username=request.data.get("email"), password=request.data.get("password")
        )
        if user is not None:
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)

            email_verification_helper.send_verification_link(
                user.email,
                verification_link=f"{BASE_URL}/activate/{uidb64}/{token}"
            )

            return Response({"message": "email verification link sent"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "user not found"}, status=status.HTTP_400_BAD_REQUEST)


# 일반 이메일 로그인
class EmailLoginAPIView(APIView):
    permission_classes = ( permissions.AllowAny, )

    def post(self, request):
        user = authenticate(
            username=request.data.get("email"), password=request.data.get("password")
        )
        if user is not None:
            token = TokenObtainPairSerializer.get_token(user)
            refresh_token = str(token)
            access_token = str(token.access_token)
            res = Response(
                {
                    "user": {
                        "username": user.username,
                        "password": user.password,
                    },
                    "message": "Successfully logged in",
                    "token": {
                        "refresh": refresh_token,
                        "access": access_token,
                    },
                },
                status=status.HTTP_200_OK,
            )
            res.set_cookie("access", access_token, httponly=True)
            res.set_cookie("refresh", refresh_token, httponly=True)
            return res
        else:
            return Response(
                {"message": "Invalid User"}, status=status.HTTP_400_BAD_REQUEST
            )


class GoogleLoginCallBackView(APIView):
    def get(self, request):
        print(dict(request.GET))
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
            token_res = requests.post(
                GOOGLE_TOKEN_URI, data=token_body)
            token_res_data = token_res.json()
        except:
            return Response(
                {"error_msg": "토큰 발급 실패"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # token 이용해서 email 정보 획득
        access_token = token_res_data.get("access_token")
        try:
            email_res = requests.get(
                f'{GOOGLE_EMAIL_URI}?access_token={access_token}'
            )
            email_res_data = email_res.json()
            print(email_res_data)
        except:
            return Response(
                {"error_msg": "이메일 정보 획득 실패"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 이메일 확인해서 회원가입 / 로그인 진행
        email = email_res_data.get('email')
        try:
            user = User.objects.get(email=email)
            # 로그인
            print('login')
            social_user = SocialAccount.objects.get(user=user)
            login_body = {
                'access_token': access_token,
                'code': code
            }
            login_res = requests.post(GOOGLE_LOGIN_URI, data=login_body)
            print(login_res.json())
            if login_res.status_code == 200:  # 로그인 성공
                #  토큰 부여
                token = TokenObtainPairSerializer.get_token(user)
                refresh_token = str(token)
                access_token = str(token.access_token)
                return Response({
                    "token": {
                        "access_token": access_token,
                        "refresh_token": refresh_token
                    },

                }, status=status.HTTP_200_OK)
            else:  # 로그인 실패
                return Response(login_res.json(), status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            # 회원가입
            signup_body = {
                'access_token': access_token,
                'code': code
            }
            signup_res = requests.post(GOOGLE_LOGIN_URI, data=signup_body)
            if signup_res.status_code == 200:  # 회원가입 성공
                user = User.objects.get(email=email)
                token = TokenObtainPairSerializer.get_token(user)
                refresh_token = str(token)
                access_token = str(token.access_token)
                return Response({
                    "token": {
                        "access_token": access_token,
                        "refresh_token": refresh_token
                    },

                }, status=status.HTTP_200_OK)
            else:  # 회원가입 실패
                return Response(signup_res.json(), status=status.HTTP_400_BAD_REQUEST)


class GoogleLoginView(SocialLoginView):
    adapter_class = google_view.GoogleOAuth2Adapter
    callback_url = REDIRECT_URI
    client_class = OAuth2Client


class TestAuthView(APIView):
    # 로그인 했을때만 가능한 요청
    permission_classes = (
        permissions.IsAuthenticated,
    )

    def get(self, request):
        return Response("Success", status=status.HTTP_200_OK)
