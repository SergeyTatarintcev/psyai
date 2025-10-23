from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import PhotoAnalysis
from .serializers import PhotoAnalysisSerializer
from chat.models import Dialog, Message  # ← добавили
from chat.services import generate_ai_reply  # ← добавили

class PhotoAnalysisListCreateView(generics.ListCreateAPIView):
    queryset = PhotoAnalysis.objects.all().order_by("-created_at")
    serializer_class = PhotoAnalysisSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        obj = serializer.save()
        if obj.dialog_id:
            dialog = Dialog.objects.get(pk=obj.dialog_id)

            # создаём системное сообщение с результатом
            base_content = f"📷 Клиент загрузил фото. Анализ эмоций: {obj.result_label} ({obj.result_score})."
            Message.objects.create(dialog=dialog, role="assistant", content=base_content)

            # генерируем короткий комментарий от ИИ-психолога
            try:
                from chat.services import generate_photo_comment
                ai_text = generate_photo_comment(obj.result_label, obj.result_score)
                Message.objects.create(dialog=dialog, role="assistant", content=ai_text)
            except Exception as e:
                print("⚠️ Ошибка при генерации комментария:", e)
