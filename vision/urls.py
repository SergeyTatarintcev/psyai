
from django.urls import path
from .views import PhotoAnalysisListCreateView

urlpatterns = [
    path("photos/", PhotoAnalysisListCreateView.as_view(), name="vision-photos"),
]
