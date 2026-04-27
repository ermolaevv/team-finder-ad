import io
import random

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.files.base import ContentFile
from django.db import models
from PIL import Image, ImageDraw, ImageFont

from .managers import UserManager


AVATAR_COLORS = [
    "#4A90D9", "#7B68EE", "#5F9EA0", "#3CB371", "#CD853F",
    "#D2691E", "#20B2AA", "#6495ED", "#DB7093", "#9370DB",
    "#2E8B57", "#FF8C00", "#8B4513", "#4682B4", "#708090",
]


def generate_avatar(letter: str) -> ContentFile:
    size = 200
    color = random.choice(AVATAR_COLORS)
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


class Skill(models.Model):
    name = models.CharField(max_length=124, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=124)
    surname = models.CharField(max_length=124)
    avatar = models.ImageField(upload_to="avatars/", blank=True)
    phone = models.CharField(max_length=12, blank=True, default="")
    github_url = models.URLField(blank=True, default="")
    about = models.TextField(max_length=256, blank=True, default="")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    skills = models.ManyToManyField(Skill, blank=True, related_name="users")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    objects = UserManager()

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.name} {self.surname} <{self.email}>"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.avatar:
            letter = self.name[0] if self.name else "U"
            avatar_content = generate_avatar(letter)
            self.avatar.save(f"avatar_{self.pk}.png", avatar_content, save=True)
