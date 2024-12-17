from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class Command(BaseCommand):
    help = 'Check user credentials'

    def handle(self, *args, **options):
        # Проверяем существование пользователя
        try:
            user = User.objects.get(username='danil')
            self.stdout.write(f'User found: {user.username}')
            self.stdout.write(f'Is active: {user.is_active}')
            self.stdout.write(f'Is staff: {user.is_staff}')
            self.stdout.write(f'Is superuser: {user.is_superuser}')
            
            # Пробуем аутентифицировать
            auth_user = authenticate(username='danil', password='admin123')
            if auth_user:
                self.stdout.write(self.style.SUCCESS('Authentication successful'))
            else:
                self.stdout.write(self.style.ERROR('Authentication failed'))
                
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('User danil not found')) 