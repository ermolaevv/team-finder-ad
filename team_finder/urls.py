from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", lambda request: redirect("projects:project_list")),
    path("projects/", include("projects.urls", namespace="projects")),
    path("users/", include("users.urls", namespace="users")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
