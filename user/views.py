from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model, authenticate
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.google import views as google_view
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from .serializers import UserSerializer
import requests
from project.settings.base import BASE_URL, CLIENT_ID, CLIENT_SECRET
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# Create your views here.
GOOGLE_TOKEN_URI = "https://oauth2.googleapis.com/token"
GOOGLE_EMAIL_URI = "https://www.googleapis.com/oauth2/v1/tokeninfo"
GOOGLE_LOGIN_URI = BASE_URL + '/api/google/login'
REDIRECT_URI = BASE_URL + "/api/google/callback"
User = get_user_model()


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
