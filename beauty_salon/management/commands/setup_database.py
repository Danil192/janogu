from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from beauty_salon.models import Client, Service, Master, Appointment
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Setup initial database'

    def handle(self, *args, **options):
        # Очищаем базу
        User.objects.all().delete()
        Client.objects.all().delete()
        Service.objects.all().delete()
        Master.objects.all().delete()
        Appointment.objects.all().delete()

        # Создаем пользователей
        admin_user = User.objects.create_superuser(
            username='danil',
            password='admin123',
            email='admin@example.com'
        )

        user = User.objects.create_user(
            username='user',
            password='user123',
            email='user@example.com'
        )

        # Создаем услуги
        services = [
            Service.objects.create(
                name='Стрижка',
                price=1000,
                duration=60,
            ),
            Service.objects.create(
                name='Окрашивание',
                price=3000,
                duration=120,
            ),
            Service.objects.create(
                name='Маникюр',
                price=1500,
                duration=90,
            ),
        ]

        # Создаем мастеров
        masters = [
            Master.objects.create(
                name='Иванова Анна',
                specialization='Парикмахер',
            ),
            Master.objects.create(
                name='Петрова Мария',
                specialization='Колорист',
            ),
            Master.objects.create(
                name='Сидорова Елена',
                specialization='Мастер маникюра',
            ),
        ]

        # Добавляем услуги мастерам
        for master in masters:
            master.services.add(random.choice(services))

        # Создаем клиентов
        client1 = Client.objects.create(
            user=admin_user,
            name='Данил Админов',
            phone='+7(999)111-11-11',
            email='admin@example.com',
            service=random.choice(services)
        )

        client2 = Client.objects.create(
            user=user,
            name='Иван Пользователев',
            phone='+7(999)222-22-22',
            email='user@example.com',
            service=random.choice(services)
        )

        # Создаем записи
        now = datetime.now()
        for i in range(5):
            Appointment.objects.create(
                client=client1,
                service=random.choice(services),
                master=random.choice(masters),
                date=now + timedelta(days=i)
            )

            Appointment.objects.create(
                client=client2,
                service=random.choice(services),
                master=random.choice(masters),
                date=now + timedelta(days=i)
            )

        self.stdout.write(self.style.SUCCESS('Database setup completed successfully')) 