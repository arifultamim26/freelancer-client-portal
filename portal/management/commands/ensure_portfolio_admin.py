import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create the configured portfolio superuser if it does not already exist."

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "portfolio-admin")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "")
        if not email or not password:
            self.stdout.write("Skipping portfolio admin creation; credentials are not configured.")
            return

        user_model = get_user_model()
        existing = user_model.objects.filter(**{user_model.USERNAME_FIELD: username}).first()
        if existing:
            if not existing.is_superuser:
                raise CommandError(f"The configured username {username!r} already exists without superuser access.")
            self.stdout.write("Configured portfolio superuser already exists; leaving it unchanged.")
            return

        user_model.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write("Created the configured portfolio superuser.")
