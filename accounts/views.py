from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.contrib.auth.decorators import login_required

@csrf_exempt
def register_user(request):
    """Регистрация по email и паролю."""
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"error": "Некорректный JSON"}, status=400)

    email = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()

    if not email or not password:
        return JsonResponse({"error": "Укажите почту и пароль"}, status=400)

    if User.objects.filter(username=email).exists():
        return JsonResponse({"error": "Такой пользователь уже зарегистрирован"}, status=400)

    user = User.objects.create_user(username=email, email=email, password=password)
    login(request, user)
    return JsonResponse({"success": True, "message": "Регистрация выполнена", "email": email})

@login_required
def me(request):
    user = request.user
    return JsonResponse({
        "email": user.email,
        "id": user.id,
        "is_authenticated": True
    })