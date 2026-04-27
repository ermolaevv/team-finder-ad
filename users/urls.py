from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("list/", views.participants, name="participants"),
    path("edit-profile/", views.edit_profile, name="edit_profile"),
    path("change-password/", views.change_password, name="change_password"),
    path("skills/", views.skill_autocomplete, name="skill_autocomplete"),
    path("<int:user_id>/", views.user_detail, name="user_detail"),
    path("<int:user_id>/skills/add/", views.add_user_skill, name="add_user_skill"),
    path(
        "<int:user_id>/skills/<int:skill_id>/remove/",
        views.remove_user_skill,
        name="remove_user_skill",
    ),
]
