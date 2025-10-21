# chat/views.py
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import Dialog, Message
from .serializers import DialogSerializer, MessageSerializer
from .services import generate_ai_reply   # ← добавили импорт


class DialogListCreateView(generics.ListCreateAPIView):
    queryset = Dialog.objects.all().order_by("-created_at")
    serializer_class = DialogSerializer
    permission_classes = [AllowAny]

class MessageListCreateView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        dialog_id = self.kwargs["dialog_id"]
        return Message.objects.filter(dialog_id=dialog_id).order_by("created_at")

    def perform_create(self, serializer):
        dialog_id = self.kwargs["dialog_id"]
        msg = serializer.save(dialog_id=dialog_id)
        # если это сообщение пользователя — вызываем ИИ и добавляем ответ
        if msg.role == "user":
            dialog = Dialog.objects.get(pk=dialog_id)
            generate_ai_reply(dialog)
