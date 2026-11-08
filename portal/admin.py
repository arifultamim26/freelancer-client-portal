from django.contrib import admin
from .models import Deliverable, Feedback, Invoice, Milestone, Profile, Project


class MilestoneInline(admin.TabularInline):
    model = Milestone
    extra = 0


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "client", "freelancer", "status", "due_date")
    list_filter = ("status",)
    search_fields = ("title", "client__username", "freelancer__username")
    inlines = (MilestoneInline,)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role")
    list_filter = ("role",)
    search_fields = ("user__username", "user__email")


@admin.register(Deliverable)
class DeliverableAdmin(admin.ModelAdmin):
    list_display = ("title", "project", "milestone", "created_at")
    search_fields = ("title", "project__title")


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("reference", "project", "amount", "status", "due_date")
    list_filter = ("status",)
    search_fields = ("reference", "project__title")


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("project", "milestone", "author", "created_at")
