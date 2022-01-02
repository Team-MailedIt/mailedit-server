from django.urls import path
from .views import *

urlpatterns = [
    path("signup", EmailRegisterAPIView.as_view()),
]
