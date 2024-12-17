from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Reset passwords for test users'

    def handle(self, *args, **options):
        # Сброс пароля для admin
        try:
            admin = User.objects.get(username='danil')
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(self.style.SUCCESS(f'Reset password for danil'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User danil not found'))

        # Сброс пароля для user
        try:
            user = User.objects.get(username='user')
            user.set_password('user123')
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Reset password for user'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User user not found')) 