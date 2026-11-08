from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Feedback, Milestone, Profile, Project


class PortalAccessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.freelancer = User.objects.create_user(username="freelancer", password="safe-demo-pass")
        Profile.objects.create(user=cls.freelancer, role=Profile.Role.FREELANCER)
        cls.client_user = User.objects.create_user(username="client-a", password="safe-demo-pass")
        Profile.objects.create(user=cls.client_user, role=Profile.Role.CLIENT)
        cls.other_client = User.objects.create_user(username="client-b", password="safe-demo-pass")
        Profile.objects.create(user=cls.other_client, role=Profile.Role.CLIENT)
        cls.project = Project.objects.create(title="Brand refresh", summary="A sample project", freelancer=cls.freelancer, client=cls.client_user)
        cls.other_project = Project.objects.create(title="Website update", summary="Another sample", freelancer=cls.freelancer, client=cls.other_client)
        cls.milestone = Milestone.objects.create(project=cls.project, title="First concept")
        cls.other_milestone = Milestone.objects.create(project=cls.other_project, title="Discovery")

    def test_dashboard_requires_sign_in(self):
        response = self.client.get(reverse("dashboard"))
        self.assertRedirects(response, f"{reverse('login')}?next=/")

    def test_client_only_sees_assigned_project(self):
        self.client.login(username="client-a", password="safe-demo-pass")
        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, "Brand refresh")
        self.assertNotContains(response, "Website update")

    def test_freelancer_only_sees_owned_projects(self):
        second_freelancer = User.objects.create_user(username="other-freelancer", password="safe-demo-pass")
        Project.objects.create(title="Not mine", summary="Private project", freelancer=second_freelancer, client=self.other_client)
        self.client.login(username="freelancer", password="safe-demo-pass")
        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, "Brand refresh")
        self.assertContains(response, "Website update")
        self.assertNotContains(response, "Not mine")

    def test_client_cannot_open_another_clients_project(self):
        self.client.login(username="client-a", password="safe-demo-pass")
        response = self.client.get(reverse("project_detail", args=[self.other_project.id]))
        self.assertEqual(response.status_code, 404)

    def test_assigned_client_can_view_project_sections(self):
        self.client.login(username="client-a", password="safe-demo-pass")
        response = self.client.get(reverse("project_detail", args=[self.project.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Milestones")
        self.assertContains(response, "Deliverables")
        self.assertContains(response, "Feedback")

    def test_milestone_status_changes_update_project_progress(self):
        second_milestone = Milestone.objects.create(project=self.project, title="Final delivery", position=1)
        self.milestone.status = Milestone.Status.COMPLETE
        self.milestone.save()
        self.assertEqual(self.project.progress_percent, 50)
        second_milestone.status = Milestone.Status.COMPLETE
        second_milestone.save()
        self.assertEqual(self.project.progress_percent, 100)

    def test_freelancer_cannot_open_project_owned_by_another_freelancer(self):
        other_freelancer = User.objects.create_user(username="other-freelancer", password="safe-demo-pass")
        foreign = Project.objects.create(title="Private work", summary="Private", freelancer=other_freelancer, client=self.other_client)
        self.client.login(username="freelancer", password="safe-demo-pass")
        self.assertEqual(self.client.get(reverse("project_detail", args=[foreign.id])).status_code, 404)

    def test_assigned_client_can_leave_feedback_and_author_is_from_session(self):
        self.client.login(username="client-a", password="safe-demo-pass")
        response = self.client.post(reverse("add_feedback", args=[self.project.id]), {"milestone": self.milestone.id, "message": "Looks good"})
        self.assertRedirects(response, reverse("project_detail", args=[self.project.id]))
        feedback = Feedback.objects.get(project=self.project)
        self.assertEqual(feedback.author, self.client_user)
        self.assertEqual(feedback.milestone, self.milestone)

    def test_client_cannot_attach_feedback_to_another_projects_milestone(self):
        self.client.login(username="client-a", password="safe-demo-pass")
        response = self.client.post(reverse("add_feedback", args=[self.project.id]), {"milestone": self.other_milestone.id, "message": "Cross-project attempt"})
        self.assertRedirects(response, reverse("project_detail", args=[self.project.id]))
        self.assertFalse(Feedback.objects.exists())

    def test_freelancer_cannot_post_client_feedback(self):
        self.client.login(username="freelancer", password="safe-demo-pass")
        self.client.post(reverse("add_feedback", args=[self.project.id]), {"milestone": self.milestone.id, "message": "Impersonated feedback"})
        self.assertFalse(Feedback.objects.exists())
