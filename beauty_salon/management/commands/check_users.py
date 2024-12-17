from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Check existing users'

    def handle(self, *args, **options):
        users = User.objects.all()
        for user in users:
            self.stdout.write(
                f'Username: {user.username}, '
                f'Is staff: {user.is_staff}, '
                f'Is superuser: {user.is_superuser}, '
                f'Is active: {user.is_active}'
            ) 