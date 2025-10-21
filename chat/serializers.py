from rest_framework import serializers
from .models import Dialog, Message

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "role", "content", "created_at"]

class DialogSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Dialog
        fields = ["id", "title", "created_at", "updated_at", "messages"]
