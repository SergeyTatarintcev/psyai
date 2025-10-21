from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import PhotoAnalysis
from .serializers import PhotoAnalysisSerializer

class PhotoAnalysisListCreateView(generics.ListCreateAPIView):
    queryset = PhotoAnalysis.objects.all().order_by("-created_at")
    serializer_class = PhotoAnalysisSerializer
    permission_classes = [AllowAny]
