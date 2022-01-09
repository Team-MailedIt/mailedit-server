from django.urls import path
from .views import *

urlpatterns = [
    path("templates/my", MyTemplateListView.as_view()),
    path("templates/base", BaseTemplateListView.as_view()),
    path("templates/<str:pk>", TemplateDetailView.as_view()),
    path("groups/", GroupListView.as_view()),
    path("groups/<int:id>", GroupDetailView.as_view()),
]
