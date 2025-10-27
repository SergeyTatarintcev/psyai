# accounts/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",   # доступ: user.profile
    )
    is_paid = models.BooleanField(default=False)
    free_messages_used = models.PositiveIntegerField(default=0)
    free_messages_limit = models.PositiveIntegerField(default=10)

    def __str__(self):
        return f"Profile<{self.user.username}> paid={self.is_paid} used={self.free_messages_used}/{self.free_messages_limit}"


@receiver(post_save, sender=User)
def create_profile_for_user(sender, instance, created, **kwargs):
    """Автосоздание профиля при создании пользователя."""
    if created:
        Profile.objects.create(user=instance)
