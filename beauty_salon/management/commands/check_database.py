from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from beauty_salon.models import Client, Service, Master, Appointment

class Command(BaseCommand):
    help = 'Check database state'

    def handle(self, *args, **options):
        # Проверяем таблицы
        self.stdout.write('Checking database tables...')
        
        # Проверяем пользователей
        user_count = User.objects.count()
        self.stdout.write(f'Users count: {user_count}')
        
        # Проверяем услуги
        service_count = Service.objects.count()
        self.stdout.write(f'Services count: {service_count}')
        
        # Проверяем мастеров
        master_count = Master.objects.count()
        self.stdout.write(f'Masters count: {master_count}')
        
        # Проверяем клиентов
        client_count = Client.objects.count()
        self.stdout.write(f'Clients count: {client_count}')
        
        # Проверяем записи
        appointment_count = Appointment.objects.count()
        self.stdout.write(f'Appointments count: {appointment_count}') 