from django.urls import path
from .views import DialogListCreateView, MessageListCreateView

urlpatterns = [
    path("dialogs/", DialogListCreateView.as_view(), name="dialog-list"),
    path("dialogs/<int:dialog_id>/messages/", MessageListCreateView.as_view(), name="message-list"),
]
