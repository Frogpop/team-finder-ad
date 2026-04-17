from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("list/", views.UserListView.as_view(), name="list"),
    path("<int:pk>/", views.UserDetailView.as_view(), name="detail"),
    path("edit-profile/", views.ProfileUpdateView.as_view(), name="edit_profile"),
    path("change-password/", views.PasswordChangeView.as_view(), name="change_password"),
]