from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from beauty_salon.models import Client

class Command(BaseCommand):
    help = 'Links existing clients with users'

    def handle(self, *args, **options):
        clients = Client.objects.filter(user__isnull=True)
        for client in clients:
            # Создаем пользователя на основе email клиента
            username = client.email.split('@')[0]
            user = User.objects.create_user(
                username=username,
                email=client.email,
                password='password123'  # временный пароль
            )
            client.user = user
            client.save()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully linked client {client.name} with user {user.username}')
            ) 