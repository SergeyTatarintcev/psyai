from rest_framework import serializers
from .models import PhotoAnalysis
from .services import analyze_emotions  # вызов заглушки-анализа

class PhotoAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhotoAnalysis
        fields = ["id", "image", "notes", "result_label", "result_score", "created_at"]
        read_only_fields = ["result_label", "result_score", "created_at"]

    def create(self, validated_data):
        obj = super().create(validated_data)
        label, score = analyze_emotions(obj.image.path)
        obj.result_label = label
        obj.result_score = score
        obj.save(update_fields=["result_label", "result_score"])
        return obj
