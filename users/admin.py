from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Skill, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "name", "surname", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active")
    search_fields = ("email", "name", "surname")
    ordering = ("email",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal info",
            {"fields": ("name", "surname", "avatar", "phone", "github_url", "about")},
        ),
        ("Skills", {"fields": ("skills",)}),
        (
            "Permissions",
            {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "name", "surname", "password1", "password2"),
            },
        ),
    )
    filter_horizontal = ("skills", "groups", "user_permissions")


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
