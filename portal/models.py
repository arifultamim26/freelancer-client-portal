from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Profile(models.Model):
    class Role(models.TextChoices):
        FREELANCER = "freelancer", "Freelancer"
        CLIENT = "client", "Client"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=12, choices=Role.choices, default=Role.CLIENT)

    def __str__(self):
        return f"{self.user.get_username()} ({self.get_role_display()})"


class Project(models.Model):
    class Status(models.TextChoices):
        PLANNING = "planning", "Planning"
        ACTIVE = "active", "In progress"
        REVIEW = "review", "In review"
        COMPLETED = "completed", "Completed"
        ON_HOLD = "on_hold", "On hold"

    title = models.CharField(max_length=140)
    summary = models.TextField()
    freelancer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="freelance_projects")
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="client_projects")
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PLANNING)
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at", "title"]

    def __str__(self):
        return self.title

    @property
    def progress_percent(self):
        total = self.milestones.count()
        if not total:
            return 0
        complete = self.milestones.filter(status=Milestone.Status.COMPLETE).count()
        return round(complete * 100 / total)

    @classmethod
    def visible_to(cls, user):
        return cls.objects.filter(models.Q(freelancer=user) | models.Q(client=user)).distinct()


class Milestone(models.Model):
    class Status(models.TextChoices):
        UPCOMING = "upcoming", "Upcoming"
        IN_PROGRESS = "in_progress", "In progress"
        NEEDS_REVIEW = "needs_review", "Needs review"
        COMPLETE = "complete", "Complete"

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="milestones")
    title = models.CharField(max_length=140)
    description = models.TextField(blank=True)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.UPCOMING)
    position = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["position", "due_date", "id"]

    def __str__(self):
        return f"{self.project}: {self.title}"


class Deliverable(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="deliverables")
    milestone = models.ForeignKey(Milestone, on_delete=models.SET_NULL, null=True, blank=True, related_name="deliverables")
    title = models.CharField(max_length=140)
    url = models.URLField(max_length=500)
    notes = models.CharField(max_length=240, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Invoice(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SENT = "sent", "Sent"
        PAID = "paid", "Paid"
        OVERDUE = "overdue", "Overdue"

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="invoices")
    reference = models.CharField(max_length=40)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=8, choices=Status.choices, default=Status.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-due_date", "reference"]
        constraints = [models.UniqueConstraint(fields=["project", "reference"], name="unique_invoice_reference_per_project")]

    def __str__(self):
        return self.reference


class Feedback(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="feedback")
    milestone = models.ForeignKey(Milestone, on_delete=models.SET_NULL, null=True, blank=True, related_name="feedback")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="portal_feedback")
    message = models.TextField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Feedback by {self.author} on {self.project}"
