from django.urls import path
from .views import *
urlpatterns = [
    path("signup", SignUpAPIView.as_view()),
]
