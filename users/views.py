import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from .forms import ChangePasswordForm, EditProfileForm, LoginForm, RegisterForm
from .models import Skill, User


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            User.objects.create_user(
                email=form.cleaned_data["email"],
                name=form.cleaned_data["name"],
                surname=form.cleaned_data["surname"],
                password=form.cleaned_data["password"],
            )
            return redirect("users:login")
    else:
        form = RegisterForm()
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
            )
            if user is not None:
                login(request, user)
                return redirect("projects:project_list")
            form.add_error(None, "Неверный имейл или пароль")
    else:
        form = LoginForm()
    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("projects:project_list")


def user_detail(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    return render(request, "users/user-details.html", {"user": user})


@login_required
def edit_profile(request):
    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("users:user_detail", user_id=request.user.pk)
    else:
        form = EditProfileForm(instance=request.user)
    return render(request, "users/edit_profile.html", {"form": form})


@login_required
def change_password(request):
    if request.method == "POST":
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            request.user.set_password(form.cleaned_data["new_password1"])
            request.user.save()
            login(request, request.user)
            return redirect("users:user_detail", user_id=request.user.pk)
    else:
        form = ChangePasswordForm(request.user)
    return render(request, "users/change_password.html", {"form": form})


def participants(request):
    queryset = User.objects.all().order_by("-id")
    active_skill = request.GET.get("skill", "").strip()

    if active_skill:
        queryset = queryset.filter(skills__name=active_skill)

    all_skills = Skill.objects.all().order_by("name")

    paginator = Paginator(queryset, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "users/participants.html",
        {
            "participants": page_obj,
            "all_skills": all_skills,
            "active_skill": active_skill,
        },
    )


@require_GET
def skill_autocomplete(request):
    q = request.GET.get("q", "").strip()
    skills = Skill.objects.filter(name__istartswith=q).order_by("name")[:10]
    data = list(skills.values("id", "name"))
    return JsonResponse(data, safe=False)


@login_required
@require_POST
def add_user_skill(request, user_id):
    if request.user.pk != user_id:
        return JsonResponse({"error": "Forbidden"}, status=403)
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        body = {}

    skill_id = body.get("skill_id")
    name = body.get("name", "").strip()

    created = False
    if skill_id:
        skill = get_object_or_404(Skill, pk=skill_id)
    elif name:
        skill, created = Skill.objects.get_or_create(name=name)
    else:
        return JsonResponse({"error": "No skill_id or name provided"}, status=400)

    added = False
    if skill not in request.user.skills.all():
        request.user.skills.add(skill)
        added = True

    return JsonResponse(
        {"skill_id": skill.pk, "name": skill.name, "created": created, "added": added}
    )


@login_required
@require_POST
def remove_user_skill(request, user_id, skill_id):
    if request.user.pk != user_id:
        return JsonResponse({"error": "Forbidden"}, status=403)
    skill = get_object_or_404(Skill, pk=skill_id)
    if not request.user.skills.filter(pk=skill_id).exists():
        return JsonResponse({"error": "Skill not in user profile"}, status=400)
    request.user.skills.remove(skill)
    return JsonResponse({"status": "ok"})
