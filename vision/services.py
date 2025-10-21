from PIL import Image, ImageStat

def analyze_emotions(image_path: str) -> tuple[str, float]:
    """
    Простейшая заглушка: считаем среднюю яркость картинки и маппим на 'positive/neutral/low'.
    Потом заменим на реальную модель/вызов ИИ с vision.
    """
    try:
        img = Image.open(image_path).convert("L")  # grayscale
        stat = ImageStat.Stat(img)
        brightness = stat.mean[0] / 255.0  # 0..1
    except Exception:
        # если что-то пошло не так — вернём neutral
        return "neutral", 0.5

    # Очень грубое правило: ярче картинка → "позитивнее" (только для MVP-демо)
    if brightness >= 0.66:
        return "positive", round(brightness, 2)
    elif brightness <= 0.33:
        return "low", round(1 - brightness, 2)
    else:
        return "neutral", 0.6
