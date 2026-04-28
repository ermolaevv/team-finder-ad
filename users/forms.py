from django import forms

from team_finder.utils import validate_phone
from .models import User

MAX_NAME_LENGTH = 124


class RegisterForm(forms.Form):
    name = forms.CharField(
        max_length=MAX_NAME_LENGTH,
        label="Имя",
        widget=forms.TextInput(attrs={"placeholder": "Имя"}),
    )
    surname = forms.CharField(
        max_length=MAX_NAME_LENGTH,
        label="Фамилия",
        widget=forms.TextInput(attrs={"placeholder": "Фамилия"}),
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "Email"}),
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"placeholder": "Пароль"}),
    )

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует.")
        return email

    def save(self):
        return User.objects.create_user(
            email=self.cleaned_data["email"],
            name=self.cleaned_data["name"],
            surname=self.cleaned_data["surname"],
            password=self.cleaned_data["password"],
        )


class LoginForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "Email"}),
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"placeholder": "Пароль"}),
    )


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["name", "surname", "avatar", "about", "phone", "github_url"]
        labels = {
            "name": "Имя",
            "surname": "Фамилия",
            "avatar": "Аватар",
            "about": "О себе",
            "phone": "Телефон",
            "github_url": "GitHub",
        }
        widgets = {
            "avatar": forms.FileInput(),
            "about": forms.Textarea(attrs={"rows": 4}),
            "phone": forms.TextInput(attrs={"placeholder": "+7XXXXXXXXXX или 8XXXXXXXXXX"}),
            "github_url": forms.URLInput(attrs={"placeholder": "https://github.com/username"}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()
        if not phone:
            return phone
        phone = validate_phone(phone)
        qs = User.objects.filter(phone=phone)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(
                "Этот номер телефона уже используется другим пользователем."
            )
        return phone

    def clean_github_url(self):
        url = self.cleaned_data.get("github_url", "").strip()
        if not url:
            return url
        if "github.com" not in url:
            raise forms.ValidationError("Ссылка должна вести на GitHub (github.com).")
        return url


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(
        label="Текущий пароль",
        widget=forms.PasswordInput(),
    )
    new_password1 = forms.CharField(
        label="Новый пароль",
        widget=forms.PasswordInput(),
    )
    new_password2 = forms.CharField(
        label="Подтвердите новый пароль",
        widget=forms.PasswordInput(),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise forms.ValidationError("Неверный текущий пароль.")
        return old_password

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("new_password1")
        p2 = cleaned.get("new_password2")
        if p1 and p2 and p1 != p2:
            self.add_error("new_password2", "Пароли не совпадают.")
        return cleaned
