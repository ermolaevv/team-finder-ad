from django import forms

from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description", "github_url", "status"]
        labels = {
            "name": "Название проекта",
            "description": "Описание проекта",
            "github_url": "Ссылка на GitHub",
            "status": "Статус",
        }
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Название проекта"}),
            "description": forms.Textarea(attrs={"rows": 5, "placeholder": "Описание проекта"}),
            "github_url": forms.URLInput(attrs={"placeholder": "https://github.com/owner/repo"}),
            "status": forms.Select(choices=[("open", "Открыт"), ("closed", "Закрыт")]),
        }

    def clean_github_url(self):
        url = self.cleaned_data.get("github_url", "").strip()
        if not url:
            return url
        if "github.com" not in url:
            raise forms.ValidationError("Ссылка должна вести на GitHub (github.com).")
        return url
