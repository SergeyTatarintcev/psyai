# chat/services.py
import os
from openai import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")  # опционально
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

_client_kwargs = {"api_key": OPENAI_API_KEY}
if OPENAI_BASE_URL:
    _client_kwargs["base_url"] = OPENAI_BASE_URL

client = OpenAI(**_client_kwargs)

SYSTEM_PROMPT = (
    "Ты — эмпатичный, аккуратный в формулировках ассистент-психолог. "
    "Не ставь диагнозов, не давай медицинских рекомендаций. "
    "Помогай прояснять чувства и формулировать шаги самопомощи. "
    "Пиши кратко, уважительно, без осуждения."
)

def build_history(messages):
    """Преобразуем нашу БД-историю в формат для модели (короткий контекст)."""
    items = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in messages.order_by("created_at")[:20]:  # ограничим контекст
        items.append({"role": m.role, "content": m.content})
    return items

def generate_ai_reply(dialog):
    """Собираем историю и запрашиваем модель."""
    from .models import Message
    history = build_history(dialog.messages)
    # API Responses (современный рекомендуемый метод)
    resp = client.responses.create(
        model=OPENAI_MODEL,
        input=history,
        temperature=0.7,
        max_output_tokens=500,
    )
    text = resp.output_text or "Извини, сейчас не могу ответить."
    # сохраняем как сообщение ассистента
    return Message.objects.create(dialog=dialog, role="assistant", content=text)
