from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include

urlpatterns = [
    path("", lambda request: redirect("projects:list")),
    path("admin/", admin.site.urls),
    path("users/", include("users.urls")),
    path("projects/", include("projects.urls")),
]
