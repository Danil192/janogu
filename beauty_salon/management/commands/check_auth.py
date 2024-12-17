from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class Command(BaseCommand):
    help = 'Check authentication for specific user'

    def handle(self, *args, **options):
        username = 'danil'
        password = 'admin123'
        
        # Проверяем существование пользователя
        try:
            user = User.objects.get(username=username)
            self.stdout.write(f'Found user: {user.username}')
            self.stdout.write(f'Is active: {user.is_active}')
            self.stdout.write(f'Is staff: {user.is_staff}')
            self.stdout.write(f'Is superuser: {user.is_superuser}')
            
            # Пробуем аутентифицировать
            auth_user = authenticate(username=username, password=password)
            if auth_user:
                self.stdout.write(self.style.SUCCESS('Authentication successful'))
            else:
                self.stdout.write(self.style.ERROR('Authentication failed'))
                
            # Проверяем хеш пар��ля
            self.stdout.write(f'Password hash: {user.password}')
            
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User {username} not found')) 