
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from emails.models import EmailProcessingJob


class Command(BaseCommand):
    help = "Add an email file to the background-processing queue."

    def add_arguments(self, parser):
        parser.add_argument(
            "email_path",
            type=str,
            help="Path to the email file to queue.",
        )

    def handle(self, *args, **options):
        email_path = Path(options["email_path"]).resolve()
        project_root = Path(settings.BASE_DIR).resolve()

        # Only allow files inside the project directory.
        if not email_path.is_relative_to(project_root):
            raise CommandError(
                "The email file must be inside the project directory."
            )

        if not email_path.is_file():
            raise CommandError(
                f"Email file does not exist: {email_path}"
            )

        job = EmailProcessingJob.objects.create(
            source_path=str(email_path),
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Queued job {job.pk}: {email_path}"
            )
        )