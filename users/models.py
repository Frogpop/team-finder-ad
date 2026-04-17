from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont
import io
import random
import re


def validate_github_url(value: str):
    if value and "github.com" not in value.lower():
        raise ValidationError("Ссылка должна вести на GitHub (github.com)")


def normalize_phone(phone: str) -> str:
    cleaned = re.sub(r"[^\d+]", "", phone)
    if cleaned.startswith("8") and len(cleaned) == 11:
        cleaned = "+7" + cleaned[1:]
    return cleaned


def generate_avatar(name: str) -> ContentFile:
    bg_colors = ["#A8D8EA", "#F7CAC9", "#92A8D1", "#88B04B", "#F7786B", "#955251"]
    text_color = "#2C3E50"

    img = Image.new("RGB", (200, 200), color=random.choice(bg_colors))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 100)
    except (IOError, OSError):
        font = ImageFont.load_default()

    initial = (name[0] if name else "?").upper()
    bbox = draw.textbbox((0, 0), initial, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((200 - w) / 2, (200 - h) / 2 - 10), initial, fill=text_color, font=font)

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return ContentFile(buffer.getvalue(), name=f"avatar_{name}.png")


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email обязателен")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = None

    email = models.EmailField(unique=True, verbose_name="Email")
    name = models.CharField(max_length=124, verbose_name="Имя")
    surname = models.CharField(max_length=124, verbose_name="Фамилия")
    avatar = models.ImageField(upload_to="avatars/", verbose_name="Аватар")
    phone = models.CharField(
        max_length=12,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Телефон",
        validators=[RegexValidator(
            regex=r"^(\+7|8)\d{10}$",
            message="Формат: +7XXXXXXXXXX или 8XXXXXXXXXX"
        )],
    )
    github_url = models.URLField(blank=True, verbose_name="GitHub", validators=[validate_github_url])
    about = models.TextField(max_length=256, blank=True, verbose_name="О себе")

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Вариант 1: Избранное
    favorites = models.ManyToManyField(
        "projects.Project",
        blank=True,
        related_name="interested_users",
        verbose_name="Избранные проекты",
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["-id"]

    def __str__(self):
        return f"{self.surname} {self.name}"

    def save(self, *args, **kwargs):
        if not self.avatar and self.name and not self.pk:
            self.avatar = generate_avatar(self.name)
        if self.phone:
            self.phone = normalize_phone(self.phone)
        else:
            self.phone = None
        super().save(*args, **kwargs)
