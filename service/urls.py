from django.urls import path
from .views import *

urlpatterns = [
    path("templates/my", MyTemplateListView.as_view()),
    path("templates/base", BaseTemplateListView.as_view()),
    path("template/<str:sub_id>", TemplateDetailView.as_view()),
]