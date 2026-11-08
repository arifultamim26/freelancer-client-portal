from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from .forms import FeedbackForm
from .models import Invoice, Profile, Project


def health(request):
    return HttpResponse("ok", content_type="text/plain")


@login_required
def dashboard(request):
    projects = Project.visible_to(request.user).select_related("freelancer", "client").prefetch_related("milestones")
    try:
        role = request.user.profile.role
    except Profile.DoesNotExist:
        role = Profile.Role.FREELANCER if request.user.is_staff else Profile.Role.CLIENT
    context = {"projects": projects, "role": role, "active_count": projects.filter(status=Project.Status.ACTIVE).count(), "open_invoices": Invoice.objects.filter(project__in=projects, status__in=[Invoice.Status.SENT, Invoice.Status.OVERDUE]).count()}
    return render(request, "portal/dashboard.html", context)


@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project.visible_to(request.user).select_related("freelancer", "client").prefetch_related("milestones", "deliverables", "invoices", "feedback__author"), pk=project_id)
    return render(request, "portal/project_detail.html", {"project": project, "can_leave_feedback": request.user == project.client, "feedback_form": FeedbackForm(project=project)})


@login_required
def add_feedback(request, project_id):
    project = get_object_or_404(Project.visible_to(request.user), pk=project_id)
    if request.method != "POST":
        return redirect("project_detail", project_id=project.id)
    if request.user != project.client:
        messages.error(request, "Only the project client can leave feedback here.")
        return redirect("project_detail", project_id=project.id)
    form = FeedbackForm(request.POST, project=project)
    if form.is_valid():
        feedback = form.save(commit=False)
        feedback.project = project
        feedback.author = request.user
        feedback.save()
        messages.success(request, "Your feedback was added.")
    else:
        messages.error(request, "Please check your feedback and try again.")
    return redirect("project_detail", project_id=project.id)
