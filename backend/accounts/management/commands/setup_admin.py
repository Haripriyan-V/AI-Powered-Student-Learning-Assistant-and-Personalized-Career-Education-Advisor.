from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model
import os
from pathlib import Path


class Command(BaseCommand):
    help = 'Creates or updates the default admin superuser safely and seeds database data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force-seed',
            action='store_true',
            help='Force reloading fixtures from seed_data.json even if data exists.',
        )

    def handle(self, *args, **options):
        User = get_user_model()
        username = os.environ.get('DJANGO_ADMIN_USERNAME', 'admin')
        password = os.environ.get('DJANGO_ADMIN_PASSWORD', 'Admin@123')
        email = os.environ.get('DJANGO_ADMIN_EMAIL', 'admin@example.com')

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.role = 'admin'
        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' created successfully."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' password updated successfully."))

        # Auto-seed initial platform data (courses, careers, scholarships, colleges, questions)
        # only if the database does not already contain records, to preserve admin edits.
        seed_file = Path(__file__).resolve().parent.parent.parent.parent / 'seed_data.json'
        if seed_file.exists():
            try:
                from learning.models import Course
                has_data = Course.objects.exists()
                if not has_data or options.get('force_seed'):
                    self.stdout.write("Loading initial data from seed_data.json...")
                    call_command('loaddata', str(seed_file))
                    self.stdout.write(self.style.SUCCESS("Initial seed data loaded successfully!"))
                else:
                    self.stdout.write("Database already contains records; skipping fixture overwrite to preserve data.")
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Note on seeding data: {e}"))
