from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # 일반 이메일
    path("signup", EmailRegisterAPIView.as_view()),
    path("signin", EmailLoginAPIView.as_view()),
    path("retry_verification", RetryVerificationAPI.as_view()),
    # 소셜 로그인(구글)
    path("google/callback", GoogleLoginCallBackView.as_view()),
    path('google/login', GoogleLoginView.as_view()),
    path('token/refresh', TokenRefreshView.as_view()),
    path('test', TestAuthView.as_view()),
]
