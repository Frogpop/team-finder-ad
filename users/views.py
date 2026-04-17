from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, UpdateView, FormView

from .forms import UserRegistrationForm, UserLoginForm, ProfileForm, CustomPasswordChangeForm
from .models import CustomUser

# Константы пагинации
PAGINATION_SIZE = 12

# Константы фильтров пользователей
FILTER_OWNERS_OF_FAVORITE = "owners-of-favorite-projects"
FILTER_OWNERS_OF_PARTICIPATING = "owners-of-participating-projects"
FILTER_INTERESTED_IN_MY = "interested-in-my-projects"
FILTER_PARTICIPANTS_OF_MY = "participants-of-my-projects"


class RegisterView(FormView):
    template_name = "users/register.html"
    form_class = UserRegistrationForm
    success_url = reverse_lazy("projects:list")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)


class LoginView(FormView):
    template_name = "users/login.html"
    form_class = UserLoginForm
    success_url = reverse_lazy("projects:list")

    def form_valid(self, form):
        login(self.request, form.cleaned_data["user"])
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


def logout_view(request):
    logout(request)
    return redirect("projects:list")


class UserListView(ListView):
    model = CustomUser
    template_name = "users/participants.html"
    context_object_name = "participants"
    paginate_by = PAGINATION_SIZE
    ordering = ["-id"]

    def get_queryset(self):
        qs = super().get_queryset()
        filter_key = self.request.GET.get("filter")
        if filter_key and self.request.user.is_authenticated:
            qs = self._apply_filter(qs, filter_key)
        return qs

    def _apply_filter(self, qs, key):
        user = self.request.user

        if key == FILTER_OWNERS_OF_FAVORITE:
            # Авторы проектов, которые я добавил в избранное
            return qs.filter(owned_projects__in=user.favorites.all()).distinct()

        elif key == FILTER_OWNERS_OF_PARTICIPATING:
            # Авторы проектов, в которых я участвую
            return qs.filter(owned_projects__in=user.participated_projects.all()).distinct()

        elif key == FILTER_INTERESTED_IN_MY:
            # Пользователи, которые добавили мои проекты в избранное
            return qs.filter(favorites__project__owner=user).distinct()

        elif key == FILTER_PARTICIPANTS_OF_MY:
            # Участники моих проектов
            return qs.filter(participated_projects__owner=user).distinct()

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["active_filter"] = self.request.GET.get("filter")
        ctx["active_skill"] = None
        return ctx


class UserDetailView(DetailView):
    model = CustomUser
    template_name = "users/user-details.html"
    context_object_name = "user"


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = ProfileForm
    template_name = "users/edit_profile.html"

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["profile_user"] = self.request.user
        return ctx

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse("users:detail", kwargs={"pk": self.request.user.pk})


class PasswordChangeView(LoginRequiredMixin, FormView):
    template_name = "users/change_password.html"
    form_class = CustomPasswordChangeForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        return redirect("users:detail", pk=self.request.user.pk)
