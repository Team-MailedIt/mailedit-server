from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("signup", EmailRegisterAPIView.as_view()),
    path("signin", EmailLoginAPIView.as_view()),
    path("retry_verification", RetryVerificationAPI.as_view()),
    path("google/login", GoogleLoginAPIView.as_view()),
    path("token/refresh", TokenRefreshView.as_view()),
    path("test", TestAuthView.as_view()),
]
