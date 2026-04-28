from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from team_finder.utils import generate_avatar
from .managers import UserManager


AVATAR_COLOR_STEEL_BLUE = "#4A90D9"
AVATAR_COLOR_MEDIUM_SLATE_BLUE = "#7B68EE"
AVATAR_COLOR_CADET_BLUE = "#5F9EA0"
AVATAR_COLOR_MEDIUM_SEA_GREEN = "#3CB371"
AVATAR_COLOR_PERU = "#CD853F"
AVATAR_COLOR_CHOCOLATE = "#D2691E"
AVATAR_COLOR_LIGHT_SEA_GREEN = "#20B2AA"
AVATAR_COLOR_CORNFLOWER_BLUE = "#6495ED"
AVATAR_COLOR_PALE_VIOLET_RED = "#DB7093"
AVATAR_COLOR_MEDIUM_PURPLE = "#9370DB"
AVATAR_COLOR_SEA_GREEN = "#2E8B57"
AVATAR_COLOR_DARK_ORANGE = "#FF8C00"
AVATAR_COLOR_SADDLE_BROWN = "#8B4513"
AVATAR_COLOR_ROYAL_BLUE = "#4682B4"
AVATAR_COLOR_SLATE_GRAY = "#708090"

AVATAR_COLORS = [
    AVATAR_COLOR_STEEL_BLUE,
    AVATAR_COLOR_MEDIUM_SLATE_BLUE,
    AVATAR_COLOR_CADET_BLUE,
    AVATAR_COLOR_MEDIUM_SEA_GREEN,
    AVATAR_COLOR_PERU,
    AVATAR_COLOR_CHOCOLATE,
    AVATAR_COLOR_LIGHT_SEA_GREEN,
    AVATAR_COLOR_CORNFLOWER_BLUE,
    AVATAR_COLOR_PALE_VIOLET_RED,
    AVATAR_COLOR_MEDIUM_PURPLE,
    AVATAR_COLOR_SEA_GREEN,
    AVATAR_COLOR_DARK_ORANGE,
    AVATAR_COLOR_SADDLE_BROWN,
    AVATAR_COLOR_ROYAL_BLUE,
    AVATAR_COLOR_SLATE_GRAY,
]


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
            avatar_content = generate_avatar(letter, AVATAR_COLORS)
            self.avatar.save(f"avatar_{self.pk}.png", avatar_content, save=True)
