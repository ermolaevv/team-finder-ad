import io
import re
import random

from django import forms
from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from PIL import Image, ImageDraw, ImageFont


def paginate(request, queryset, per_page=12):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)


def normalize_phone(phone: str) -> str:
    phone = phone.strip()
    if phone.startswith("8") and len(phone) == 11:
        return "+7" + phone[1:]
    return phone


def validate_phone(phone: str) -> str:
    if not phone:
        return phone
    phone = normalize_phone(phone)
    pattern = r"^\+7\d{10}$"
    if not re.match(pattern, phone):
        raise forms.ValidationError(
            "Номер должен быть в формате +7XXXXXXXXXX или 8XXXXXXXXXX."
        )
    return phone


def generate_avatar(letter: str, colors: list) -> ContentFile:
    size = 200
    color = random.choice(colors)
    img = Image.new("RGB", (size, size), color=color)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", size=100)
    except OSError:
        font = ImageFont.load_default(size=100)
    text = letter.upper()
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (size - text_w) / 2 - bbox[0]
    y = (size - text_h) / 2 - bbox[1]
    draw.text((x, y), text, fill="white", font=font)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return ContentFile(buffer.getvalue())
