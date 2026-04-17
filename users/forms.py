import re

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password

from .models import CustomUser
from .utils import normalize_phone


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")

    class Meta:
        model = CustomUser
        fields = ("name", "surname", "email")

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if password:
            validate_password(password)
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email and password:
            user = authenticate(username=email, password=password)
            if user is None:
                raise forms.ValidationError("Неверный email или пароль")
            cleaned_data["user"] = user
        return cleaned_data


class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ("name", "surname", "avatar", "about", "phone", "github_url")

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if not phone:
            return phone

        cleaned = re.sub(r"[^\d+]", "", phone)
        if not re.match(r"^(\+7|8)\d{10}$", cleaned):
            raise forms.ValidationError(
                "Номер телефона должен быть в формате +7XXXXXXXXXX или 8XXXXXXXXXX"
            )

        normalized = "+7" + cleaned[1:] if cleaned.startswith("8") else cleaned

        qs = CustomUser.objects.filter(phone=normalized)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Этот номер телефона уже используется")
        return phone

    def clean_github_url(self):
        url = self.cleaned_data.get("github_url")
        if url and "github.com" not in url.lower():
            raise forms.ValidationError("Ссылка должна вести на GitHub (github.com)")
        return url

    def save(self, commit=True):
        phone = self.cleaned_data.get("phone")
        if phone:
            self.instance.phone = normalize_phone(phone)
        return super().save(commit=commit)


class CustomPasswordChangeForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput, label="Текущий пароль")
    new_password1 = forms.CharField(widget=forms.PasswordInput, label="Новый пароль")
    new_password2 = forms.CharField(widget=forms.PasswordInput, label="Подтверждение нового пароля")

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        password = self.cleaned_data["old_password"]
        if not self.user.check_password(password):
            raise forms.ValidationError("Неверный текущий пароль")
        return password

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("new_password1")
        p2 = cleaned.get("new_password2")

        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Пароли не совпадают")
        if p1:
            validate_password(p1, self.user)
        return cleaned

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data["new_password1"])
        if commit:
            self.user.save()
        return self.user
