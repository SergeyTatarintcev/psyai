# accounts/views.py
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from accounts.models import Profile

# DRF: токены + права для /me
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated


# --------- helpers ---------
def _json(request: HttpRequest):
    """Безопасный парсинг JSON тела; возвращает (dict|None, error|None)."""
    try:
        raw = request.body.decode("utf-8") if request.body else ""
        data = json.loads(raw) if raw else {}
        if not isinstance(data, dict):
            return None, "Некорректный JSON (ожидался объект)"
        return data, None
    except Exception:
        return None, "Некорректный JSON"


def _norm(s):
    return (s or "").strip()


# --------- endpoints ---------
@csrf_exempt
@require_POST
def register_user(request: HttpRequest):
    """Регистрация по email и паролю. Возвращает JSON и логинит сессию."""
    data, err = _json(request)
    if err:
        return JsonResponse({"error": err}, status=400)

    email = _norm(data.get("email")).lower()
    password = _norm(data.get("password"))

    if not email or not password:
        return JsonResponse({"error": "Укажите почту и пароль"}, status=400)

    if User.objects.filter(username=email).exists():
        return JsonResponse({"error": "Такой пользователь уже зарегистрирован"}, status=400)

    user = User.objects.create_user(username=email, email=email, password=password)
    login(request, user)  # сессионный вход (удобно для админки/браузера)

    return JsonResponse(
        {"success": True, "message": "Регистрация выполнена", "email": email},
        status=201,
    )


@csrf_exempt
@require_POST
def login_user(request: HttpRequest):
    """Сессионный вход по email/паролю (для браузера/админки)."""
    data, err = _json(request)
    if err:
        return JsonResponse({"error": err}, status=400)

    email = _norm(data.get("email")).lower()
    password = _norm(data.get("password"))

    if not email or not password:
        return JsonResponse({"error": "Укажите почту и пароль"}, status=400)

    user = authenticate(request, username=email, password=password)
    if user is None:
        return JsonResponse({"error": "Неверная почта или пароль"}, status=400)

    login(request, user)
    return JsonResponse({"success": True, "message": "Вход выполнен", "email": email})


@csrf_exempt
def logout_user(request: HttpRequest):
    """Выход (удаление сессии). Идempotent."""
    logout(request)
    return JsonResponse({"success": True, "message": "Выход выполнен"})


@csrf_exempt
@require_POST
def token_login(request: HttpRequest):
    """Логин с выдачей DRF-токена (для API-клиентов)."""
    data, err = _json(request)
    if err:
        return JsonResponse({"error": err}, status=400)

    email = _norm(data.get("email")).lower()
    password = _norm(data.get("password"))

    if not email or not password:
        return JsonResponse({"error": "Укажите почту и пароль"}, status=400)

    user = authenticate(request, username=email, password=password)
    if user is None:
        return JsonResponse({"error": "Неверная почта или пароль"}, status=400)

    token, _ = Token.objects.get_or_create(user=user)
    return JsonResponse({"success": True, "token": token.key}, status=200)


# DRF-вариант: работает и по сессии, и по токену
@api_view(["GET"])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def me(request):
    """Текущий пользователь (auth: Token или Session)."""
    u = request.user
    return JsonResponse(
        {
            "id": u.id,
            "email": u.email,
            "is_authenticated": True,
            "auth_via": "token" if isinstance(request.successful_authenticator, TokenAuthentication) else "session",
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def upgrade(request):
    """Включить оплату пользователю по токену (заглушка)."""
    user = request.user
    # если профиль создаётся сигналом — этот блок можно убрать
    try:
        from accounts.models import Profile  # поправь путь, если другой
        profile, _ = Profile.objects.get_or_create(user=user)
    except Exception:
        profile = getattr(user, "profile", None)

    if profile is None:
        return JsonResponse({"error": "Профиль не найден/не настроен"}, status=500)

    profile.is_paid = True
    if hasattr(profile, "free_messages_used"):
        profile.free_messages_used = 0
    profile.save()

    return JsonResponse({"success": True, "is_paid": True})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_token(request):
    """Отозвать текущий DRF-токен."""
    Token.objects.filter(user=request.user).delete()
    return JsonResponse({"success": True})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def status(request):
    """Статус профиля: тариф и счётчики."""
    user = request.user
    # гарантия наличия профиля
    from accounts.models import Profile
    profile, _ = Profile.objects.get_or_create(user=user)

    return JsonResponse({
        "email": user.email,
        "is_paid": profile.is_paid,
        "free_messages_used": profile.free_messages_used,
        "free_messages_limit": profile.free_messages_limit,
    })

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def downgrade(request):
    """Вернуть бесплатный тариф пользователю (для тестов лимита)."""
    profile, _ = Profile.objects.get_or_create(user=request.user)
    profile.is_paid = False
    # по желанию сбросить счётчик:
    profile.free_messages_used = 0
    profile.save(update_fields=["is_paid", "free_messages_used"])
    return JsonResponse({"success": True, "is_paid": False})