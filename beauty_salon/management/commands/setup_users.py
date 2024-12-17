from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from beauty_salon.models import Client

class Command(BaseCommand):
    help = 'Setup admin and regular users'

    def handle(self, *args, **options):
        # Удаляем существующих пользователей
        User.objects.all().delete()
        Client.objects.all().delete()

        # Создаем админа
        admin_user = User.objects.create_user(
            username='danil',
            password='admin123',
            is_staff=True,
            is_superuser=True
        )
        
        # Создаем обычного пользователя
        user = User.objects.create_user(
            username='user',
            password='user123',
            email='user@example.com'
        )
        
        # Создаем клиента для обычного пользователя
        Client.objects.create(
            user=user,
            name='Обычный пользователь',
            phone='+7(999)999-99-99',
            email='user@example.com'
        )

        self.stdout.write(self.style.SUCCESS('Users created successfully'))