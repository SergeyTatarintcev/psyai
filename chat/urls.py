from django.urls import path
from .views import DialogListCreateView, MessageListCreateView, ensure_my_dialog

urlpatterns = [
    path("dialogs/", DialogListCreateView.as_view(), name="dialog-list"),
    path("dialogs/<int:dialog_id>/messages/", MessageListCreateView.as_view(), name="message-list"),
    path("my/ensure/", ensure_my_dialog, name="ensure-my-dialog"),
]
