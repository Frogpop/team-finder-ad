import io
import random
import re

from PIL import Image, ImageDraw, ImageFont
from django.core.files.base import ContentFile

# Константы для валидации и нормализации телефона
PHONE_PREFIX_8 = "8"
PHONE_PREFIX_7 = "+7"
PHONE_LENGTH = 11

# Константы для генерации аватара
AVATAR_SIZE = 200
AVATAR_FONT_SIZE = 100
AVATAR_TEXT_OFFSET_Y = -10
AVATAR_PASTEL_COLORS = ["#A8D8EA", "#F7CAC9", "#92A8D1", "#88B04B", "#F7786B", "#955251"]
AVATAR_TEXT_COLOR = "#2C3E50"


def normalize_phone(phone: str) -> str:
    cleaned = re.sub(r"[^\d+]", "", phone)
    if cleaned.startswith(PHONE_PREFIX_8) and len(cleaned) == PHONE_LENGTH:
        cleaned = PHONE_PREFIX_7 + cleaned[1:]
    return cleaned


def generate_avatar(name: str) -> ContentFile:
    img = Image.new("RGB", (AVATAR_SIZE, AVATAR_SIZE), color=random.choice(AVATAR_PASTEL_COLORS))
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", AVATAR_FONT_SIZE)
    except (IOError, OSError):
        font = ImageFont.load_default()

    initial = (name[0] if name else "?").upper()
    bbox = draw.textbbox((0, 0), initial, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]

    draw.text(
        ((AVATAR_SIZE - w) / 2, (AVATAR_SIZE - h) / 2 + AVATAR_TEXT_OFFSET_Y),
        initial,
        fill=AVATAR_TEXT_COLOR,
        font=font,
    )

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return ContentFile(buffer.getvalue(), name=f"avatar_{name}.png")
