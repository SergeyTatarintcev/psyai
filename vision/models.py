from django.db import models
from chat.models import Dialog  # ← новый импорт

class PhotoAnalysis(models.Model):
    dialog = models.ForeignKey(  # ← новое поле связи с чатом
        Dialog,
        on_delete=models.CASCADE,
        related_name="photos",
        null=True,
        blank=True,
    )
    image = models.ImageField(upload_to="uploads/%Y/%m/%d/")
    notes = models.CharField(max_length=255, blank=True)   # опциональный комментарий
    result_label = models.CharField(max_length=50, blank=True)  # 'positive' | 'neutral' | 'low'
    result_score = models.FloatField(default=0)            # 0..1 — уверенность
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo #{self.pk} — {self.result_label or 'pending'}"
