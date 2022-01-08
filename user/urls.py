from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("signup", EmailRegisterAPIView.as_view()),
    path("login", EmailLoginAPIView.as_view()),
    path("retry-verification", RetryVerificationAPI.as_view()),
    path("login/google", GoogleLoginAPIView.as_view()),
    path("token/refresh", TokenRefreshView.as_view()),
    path("test", TestAuthView.as_view()),
]
