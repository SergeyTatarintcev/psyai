from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from config.views import health
from config.views import health, home
from config.views import health, home, free_question


urlpatterns = [
    path("", home, name="home"),
    path("api/free-question/", free_question, name="free-question"),
    path("api/accounts/", include("accounts.urls")),
    path("admin/", admin.site.urls),
    path("api/health/", health),
    path("api/chat/", include("chat.urls")),
    path("api/vision/", include("vision.urls")),  # ← добавили
]

# медиа для DEV
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
