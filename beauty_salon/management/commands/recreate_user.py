from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from beauty_salon.models import Client

class Command(BaseCommand):
    help = 'Recreate admin user'

    def handle(self, *args, **options):
        username = 'danil'
        password = 'admin123'
        
        # Удаляем существующего пользователя если есть
        User.objects.filter(username=username).delete()
        
        # Создаем нового пользователя
        user = User.objects.create_superuser(
            username=username,
            password=password,
            email='admin@example.com'
        )
        
        # Создаем клиента для пользователя
        Client.objects.create(
            user=user,
            name='Данил Админов',
            phone='+7(999)111-11-11',
            email='admin@example.com'
        )
        
        self.stdout.write(self.style.SUCCESS(f'User {username} created successfully')) 