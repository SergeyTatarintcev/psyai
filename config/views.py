# config/views.py
from django.utils.timezone import now
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from chat.services import client, OPENAI_MODEL, SYSTEM_PROMPT  # используем существующий клиент



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


@csrf_exempt
def free_question(request):
    """До 3 бесплатных вопросов в анонимной сессии (не сохраняем в БД)."""
    if request.method != "POST":
        return JsonResponse({"error": "POST only."}, status=405)

    import json
    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"error": "Некорректный JSON."}, status=400)

    user_text = (data.get("message") or "").strip()
    if not user_text:
        return JsonResponse({"error": "Введите вопрос."}, status=400)

    # счётчик в сессии
    cnt = request.session.get("free_q_count", 0)
    if cnt >= 3:
        return JsonResponse({
            "error": "Лимит исчерпан",
            "message": "Вы использовали 3 бесплатных вопроса. Зарегистрируйтесь, чтобы продолжить общение.",
            "need_signup": True
        }, status=403)

    # генерируем ответ
    resp = client.responses.create(
        model=OPENAI_MODEL,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text},
        ],
        max_output_tokens=300,
    )
    text = (resp.output_text or "").strip()

    # увеличиваем счётчик и сохраняем в сессии
    request.session["free_q_count"] = cnt + 1
    request.session.modified = True

    return JsonResponse({
        "answer": text,
        "remaining": max(0, 3 - (cnt + 1))  # сколько осталось
    })