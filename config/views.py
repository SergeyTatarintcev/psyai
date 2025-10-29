# config/views.py
from django.utils.timezone import now
from django.shortcuts import render
from django.http import JsonResponse

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.authentication import TokenAuthentication, SessionAuthentication

from rest_framework.response import Response
from rest_framework import status

# используем существующий клиент/модель/системный промт
from chat.services import client, OPENAI_MODEL, SYSTEM_PROMPT

# --- константы лимитов ---
GUEST_LIMIT = 3  # аноним
# для авторизованных берём из Profile: free_messages_limit (по умолчанию 10)


@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    return Response({
        "status": "ok",
        "time": now().isoformat(),
        "version": "0.1.0",
    })


def home(request):
    return render(request, "home.html")


@api_view(["POST"])
@permission_classes([AllowAny])
@authentication_classes([TokenAuthentication])
def free_question(request):
    """
    Один бесплатный вопрос:
      - Гость: лимит 3 (по сессии).
      - Авторизован и НЕ оплачено: лимит из Profile (10 по умолчанию).
      - Авторизован и оплачено: безлимит (remaining = null).
    """
    user_text = (request.data.get("message") or "").strip()
    if not user_text:
        return Response({"error": "Введите вопрос."}, status=status.HTTP_400_BAD_REQUEST)

    # --- Авторизованный пользователь ---
    if request.user.is_authenticated:
        from accounts.models import Profile  # путь корректный для нашего проекта
        profile, _ = Profile.objects.get_or_create(user=request.user)

        # оплаченный тариф — безлимит
        if profile.is_paid:
            text = _ai_answer(user_text)
            return Response({"answer": text, "remaining": None}, status=status.HTTP_200_OK)

        # бесплатный тариф — считаем по профилю (10 по умолчанию)
        remaining = max(profile.free_messages_limit - profile.free_messages_used, 0)
        if remaining <= 0:
            # 200 + флаг, чтобы фронт не падал исключением и показал оффер на апгрейд
            return Response(
                {
                    "need_upgrade": True,
                    "message": "Лимит 10 бесплатных сообщений исчерпан. Оформите подписку, чтобы продолжить."
                },
                status=status.HTTP_200_OK
            )

        text = _ai_answer(user_text)
        profile.free_messages_used += 1
        profile.save(update_fields=["free_messages_used"])
        return Response({"answer": text, "remaining": remaining - 1}, status=status.HTTP_200_OK)

    # --- Гость (аноним) ---
    used = int(request.session.get("free_q_count", 0))
    remaining_guest = max(GUEST_LIMIT - used, 0)
    if remaining_guest <= 0:
        # 403 + need_signup — чтобы фронт попал в catch и показал ссылку на регистрацию
        return Response(
            {
                "error": "Лимит исчерпан",
                "message": "Вы использовали 3 бесплатных вопроса. Зарегистрируйтесь, чтобы продолжить общение.",
                "need_signup": True
            },
            status=status.HTTP_403_FORBIDDEN
        )

    text = _ai_answer(user_text)
    request.session["free_q_count"] = used + 1
    request.session.modified = True
    return Response({"answer": text, "remaining": remaining_guest - 1}, status=status.HTTP_200_OK)


# --- helper ---
def _ai_answer(user_text: str) -> str:
    """Единая точка генерации ответа, как у тебя было."""
    resp = client.responses.create(
        model=OPENAI_MODEL,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text},
        ],
        max_output_tokens=300,
    )
    return (getattr(resp, "output_text", "") or "").strip()
