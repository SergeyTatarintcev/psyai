from django.db import models
from django.contrib.auth.models import User

class Dialog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="dialogs", null=True, blank=True)
    title = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title or f"Диалог {self.pk}"


class Message(models.Model):
    ROLE_CHOICES = [
        ("user", "Пользователь"),
        ("assistant", "ИИ"),
    ]

    dialog = models.ForeignKey(Dialog, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role}: {self.content[:50]}"
