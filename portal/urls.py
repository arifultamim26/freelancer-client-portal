from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("projects/<int:project_id>/", views.project_detail, name="project_detail"),
    path("projects/<int:project_id>/feedback/", views.add_feedback, name="add_feedback"),
    path("health/", views.health, name="health"),
]
