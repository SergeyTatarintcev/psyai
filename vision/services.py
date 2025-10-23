import os
import base64
import mimetypes
from PIL import Image, ImageStat
from openai import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
USE_VISION = os.getenv("OPENAI_USE_VISION") in ("1", "true", "True")

_client_kwargs = {"api_key": OPENAI_API_KEY} if OPENAI_API_KEY else {}
if OPENAI_BASE_URL:
    _client_kwargs["base_url"] = OPENAI_BASE_URL

client = OpenAI(**_client_kwargs) if _client_kwargs else None


def analyze_emotions(image_path: str) -> tuple[str, float]:
    """
    Если есть ключ и включён vision — спрашиваем GPT (через data URL base64),
    иначе используем заглушку по средней яркости.
    """
    if USE_VISION and client:
        try:
            mime = mimetypes.guess_type(image_path)[0] or "image/jpeg"
            with open(image_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")
            data_url = f"data:{mime};base64,{b64}"

            resp = client.responses.create(
                model="gpt-4o-mini",
                input=[
                    {
                        "role": "system",
                        "content": (
                            "Ты эмпатичный ассистент-психолог. По фото оцени общее "
                            "эмоциональное состояние одним словом: радость, грусть, тревога, "
                            "злость, спокойствие. Никаких пояснений."
                        ),
                    },
                    {
                        "role": "user",
                        "content": [{"type": "input_image", "image_url": data_url}],
                    },
                ],
                max_output_tokens=50,
            )
            text = (resp.output_text or "").strip().lower()

            if "радост" in text or "улыб" in text:
                return "positive", 0.9
            if "грусть" in text or "трев" in text:
                return "low", 0.8
            if "спок" in text:
                return "neutral", 0.7

            return (text[:20] or "neutral"), 0.5
        except Exception as e:
            print("⚠️ vision API error:", e)

    # Fallback — простая заглушка по яркости
    try:
        img = Image.open(image_path).convert("L")
        stat = ImageStat.Stat(img)
        brightness = stat.mean[0] / 255.0
    except Exception:
        return "neutral", 0.5

    if brightness >= 0.66:
        return "positive", round(brightness, 2)
    if brightness <= 0.33:
        return "low", round(1 - brightness, 2)
    return "neutral", 0.6
