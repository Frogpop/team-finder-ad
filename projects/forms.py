from django import forms

from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ("name", "description", "github_url", "status")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "status": forms.Select(choices=Project.STATUS_CHOICES),
        }

    def clean_github_url(self):
        url = self.cleaned_data.get("github_url")
        if url and "github.com" not in url.lower():
            raise forms.ValidationError("Ссылка должна вести на GitHub (github.com)")
        return url
