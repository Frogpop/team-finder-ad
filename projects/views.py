from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from .forms import ProjectForm
from .models import Project


class ProjectListView(ListView):
    model = Project
    template_name = "projects/project_list.html"
    context_object_name = "projects"
    paginate_by = 12
    ordering = ["-created_at"]


class ProjectDetailView(DetailView):
    model = Project
    template_name = "projects/project-details.html"
    context_object_name = "project"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        ctx["is_owner"] = user.is_authenticated and user == self.object.owner
        ctx["is_participant"] = user.is_authenticated and self.object.participants.filter(id=user.id).exists()
        ctx["is_favorited"] = user.is_authenticated and self.object in user.favorites.all()
        return ctx


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/create-project.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["is_edit"] = False
        return ctx

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        self.object.participants.add(self.request.user)
        return response

    def get_success_url(self):
        return reverse("projects:detail", kwargs={"pk": self.object.pk})


class ProjectUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/create-project.html"

    def test_func(self):
        return self.get_object().owner == self.request.user

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["is_edit"] = True
        return ctx

    def get_success_url(self):
        return reverse("projects:detail", kwargs={"pk": self.object.pk})


class FavoriteListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = "projects/favorite_projects.html"
    context_object_name = "projects"
    paginate_by = 12
    ordering = ["-created_at"]

    def get_queryset(self):
        return self.request.user.favorites.all()


@login_required
def toggle_favorite(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project in request.user.favorites.all():
        request.user.favorites.remove(project)
        favorited = False
    else:
        request.user.favorites.add(project)
        favorited = True
    return JsonResponse({"status": "ok", "favorited": favorited})


@login_required
def complete_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.user == project.owner and project.status == "open":
        project.status = "closed"
        project.save(update_fields=["status"])
        return JsonResponse({"status": "ok", "project_status": "closed"})
    return JsonResponse({"error": "Forbidden"}, status=403)


@login_required
def toggle_participate(request, pk):
    project = get_object_or_404(Project, pk=pk)
    user = request.user

    if user in project.participants.all():
        project.participants.remove(user)
        is_participant = False
    else:
        project.participants.add(user)
        is_participant = True

    return JsonResponse({
        "status": "ok",
        "participant": is_participant,
        "user_id": user.pk if is_participant else None,
        "user_name": f"{user.name} {user.surname}" if is_participant else None,
        "user_avatar": user.avatar.url if is_participant and user.avatar else None,
    })
