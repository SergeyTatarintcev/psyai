# chat/views.py
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .models import Dialog, Message
from .serializers import DialogSerializer, MessageSerializer
from .services import generate_ai_reply


@method_decorator(csrf_exempt, name="dispatch")
class DialogListCreateView(generics.ListCreateAPIView):
    """Список и создание диалогов (возможно, для тестов)."""
    queryset = Dialog.objects.all().order_by("-created_at")
    serializer_class = DialogSerializer
    permission_classes = [AllowAny]


@method_decorator(csrf_exempt, name="dispatch")
class MessageListCreateView(generics.ListCreateAPIView):
    """Просмотр и отправка сообщений в диалоге."""
    serializer_class = MessageSerializer
    permission_classes = [AllowAny]  # доступ проверяем вручную в perform_create

    def get_queryset(self):
        dialog_id = self.kwargs["dialog_id"]
        return Message.objects.filter(dialog_id=dialog_id).order_by("created_at")

    def perform_create(self, serializer):
        dialog_id = self.kwargs["dialog_id"]
        user = self.request.user

        if not user.is_authenticated:
            raise PermissionDenied("Только для авторизованных пользователей. Войдите или зарегистрируйтесь.")

        # проверяем лимиты профиля
        profile = getattr(user, "profile", None)
        if profile and not profile.is_paid:
            if profile.free_messages_used >= profile.free_messages_limit:
                raise PermissionDenied("Лимит бесплатных сообщений исчерпан. Оформите подписку, чтобы продолжить.")
            profile.free_messages_used += 1
            profile.save(update_fields=["free_messages_used"])

        msg = serializer.save(dialog_id=dialog_id, role="user")

        # генерируем ответ от ИИ
        if msg.role == "user":
            dialog = Dialog.objects.get(pk=dialog_id)
            generate_ai_reply(dialog)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def ensure_my_dialog(request):
    """Создать (если нет) и вернуть ID личного диалога пользователя."""
    dialog, _ = Dialog.objects.get_or_create(
        user=request.user,
        defaults={"title": "Личный диалог"}
    )
    return Response({"dialog_id": dialog.id}, status=status.HTTP_200_OK)
