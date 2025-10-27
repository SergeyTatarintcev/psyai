from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import PermissionDenied

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .models import Dialog, Message
from .serializers import DialogSerializer, MessageSerializer
from .services import generate_ai_reply


@method_decorator(csrf_exempt, name="dispatch")   # ← добавили
class DialogListCreateView(generics.ListCreateAPIView):
    queryset = Dialog.objects.all().order_by("-created_at")
    serializer_class = DialogSerializer
    permission_classes = [AllowAny]


@method_decorator(csrf_exempt, name="dispatch")   # ← добавили
class MessageListCreateView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [AllowAny]  # сам доступ дальше проверяем в perform_create

    def get_queryset(self):
        dialog_id = self.kwargs["dialog_id"]
        return Message.objects.filter(dialog_id=dialog_id).order_by("created_at")

    def perform_create(self, serializer):
        dialog_id = self.kwargs["dialog_id"]
        user = self.request.user

        if not user.is_authenticated:
            raise PermissionDenied("Только для авторизованных пользователей. Пожалуйста, войдите или зарегистрируйтесь.")

        profile = getattr(user, "profile", None)
        if profile and not profile.is_paid:
            if profile.free_messages_used >= profile.free_messages_limit:
                raise PermissionDenied("Лимит бесплатных сообщений исчерпан. Оформите подписку, чтобы продолжить.")
            profile.free_messages_used += 1
            profile.save(update_fields=["free_messages_used"])

        msg = serializer.save(dialog_id=dialog_id)

        if msg.role == "user":
            dialog = Dialog.objects.get(pk=dialog_id)
            generate_ai_reply(dialog)
