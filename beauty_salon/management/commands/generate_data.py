from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from beauty_salon.models import Service, Master, Client, Appointment, Review
from django.utils import timezone
import random
from datetime import timedelta
import faker
from django.db import transaction

class Command(BaseCommand):
    help = 'Generates large amount of test data'

    def __init__(self):
        super().__init__()
        self.fake = faker.Faker('ru_RU')
        self.services = []
        self.masters = []
        self.clients = []

    def create_services(self):
        service_templates = [
            {'name': 'Стрижка', 'price_range': (1000, 3000)},
            {'name': 'Окрашивание', 'price_range': (3000, 8000)},
            {'name': 'Маникюр', 'price_range': (1500, 3500)},
            {'name': 'Педикюр', 'price_range': (2000, 4000)},
            {'name': 'Массаж', 'price_range': (2500, 5000)},
            {'name': 'Укладка', 'price_range': (1000, 2500)},
            {'name': 'Мелирование', 'price_range': (4000, 9000)},
            {'name': 'Наращивание ресниц', 'price_range': (2000, 4000)},
            {'name': 'Макияж', 'price_range': (2000, 5000)},
            {'name': 'Эпиляция', 'price_range': (1000, 3000)},
            {'name': 'Пилинг', 'price_range': (2000, 4000)},
            {'name': 'Чистка лица', 'price_range': (2500, 5000)},
            {'name': 'Спа-процедуры', 'price_range': (3000, 7000)},
        ]

        types = ['простой', 'сложный', 'премиум', 'экспресс', 'VIP']
        zones = ['лица', 'тела', 'рук', 'ног', 'головы']
        additions = ['с уходом', 'с массажем', 'комплексный', 'аппаратный', 'классический']

        self.stdout.write('Создание услуг...')
        for template in service_templates:
            for _ in range(4):  # 4 варианта каждой услуги
                name_parts = [
                    template['name'],
                    random.choice(types),
                    random.choice(additions)
                ]
                if random.random() > 0.5:  # 50% шанс добавить зону
                    name_parts.insert(1, random.choice(zones))

                name = ' '.join(name_parts)
                min_price, max_price = template['price_range']
                
                service = Service.objects.create(
                    name=name,
                    price=random.randint(min_price, max_price),
                    duration=random.choice([30, 60, 90, 120, 150, 180])
                )
                self.services.append(service)

    def create_masters(self):
        specializations = {
            'Парикмахер': ['Стрижка', 'Укладка'],
            'Колорист': ['Окрашивание', 'Мелирование'],
            'Мастер маникюра': ['Маникюр', 'Педикюр'],
            'Косметолог': ['Чистка лица', 'Пилинг', 'Спа-процедуры'],
            'Массажист': ['Массаж'],
            'Визажист': ['Макияж'],
            'Стилист': ['Стрижка', 'Укладка', 'Окрашивание'],
            'Бровист': ['Эпиляция']
        }

        self.stdout.write('Создание мастеров...')
        for spec, related_services in specializations.items():
            # 10-15 мастеров каждой специализации
            for _ in range(random.randint(10, 15)):
                master = Master.objects.create(
                    name=self.fake.name(),
                    specialization=spec
                )
                
                # Подбираем услуги по специализации
                suitable_services = [
                    s for s in self.services 
                    if any(rs in s.name for rs in related_services)
                ]
                
                # Выбираем 3-7 услуг для мастера
                if suitable_services:
                    master.services.set(random.sample(
                        suitable_services,
                        min(random.randint(3, 7), len(suitable_services))
                    ))
                
                self.masters.append(master)

    def create_clients(self):
        self.stdout.write('Создание клиентов...')
        batch_size = 50  # Создаем по 50 клиентов за раз
        total_clients = 500
        
        for batch_start in range(0, total_clients, batch_size):
            batch_end = min(batch_start + batch_size, total_clients)
            self.stdout.write(f'Создание клиентов {batch_start+1}-{batch_end} из {total_clients}...')
            
            # Создаем пользователей пакетом
            users = []
            for i in range(batch_start, batch_end):
                user = User(
                    username=f'client{i}',
                    email=self.fake.email(),
                    is_active=True
                )
                user.set_password('password123')
                users.append(user)
            created_users = User.objects.bulk_create(users)
            
            # Создаем клиентов пакетом
            clients = []
            for user in created_users:
                client = Client(
                    user=user,
                    name=self.fake.name(),
                    phone=self.fake.phone_number(),
                    email=user.email
                )
                clients.append(client)
            
            created_clients = Client.objects.bulk_create(clients)
            self.clients.extend(created_clients)
            
            # Очищаем память
            users = []
            clients = []

    def create_appointments(self):
        self.stdout.write('Создание записей...')
        start_date = timezone.now() - timedelta(days=180)
        
        appointments = []
        for _ in range(2000):
            client = random.choice(self.clients)
            service = random.choice(self.services)
            master = random.choice([m for m in self.masters if service in m.services.all()])
            
            date = start_date + timedelta(
                days=random.randint(0, 210),
                hours=random.randint(9, 20),
                minutes=random.choice([0, 30])
            )
            
            appointments.append(Appointment(
                client=client,
                service=service,
                master=master,
                date=date
            ))
            
            if len(appointments) >= 100:
                Appointment.objects.bulk_create(appointments)
                appointments = []
        
        if appointments:
            Appointment.objects.bulk_create(appointments)

    def create_reviews(self):
        self.stdout.write('Создание отзывов...')
        positive_comments = [
            'Отличный сервис!', 'Всё понравилось', 'Рекомендую', 
            'Хороший мастер', 'Приду ещё', 'Великолепно!',
            'Всё отлично', 'Супер!', 'Очень доволен(а)', 'Спасибо большое!',
            'Профессиональная работа', 'Отличный результат'
        ]
        negative_comments = [
            'Могло быть лучше', 'Не совсем то, что ожидал(а)',
            'Есть над чем поработать', 'Среднее качество'
        ]

        reviews = []
        for _ in range(1500):
            client = random.choice(self.clients)
            service = random.choice(self.services)
            
            # 80% положительных отзывов, 20% негативных
            if random.random() < 0.8:
                rating = random.randint(4, 5)
                comment = random.choice(positive_comments)
            else:
                rating = random.randint(2, 3)
                comment = random.choice(negative_comments)
            
            reviews.append(Review(
                client=client,
                service=service,
                rating=rating,
                comment=comment,
                date=timezone.now() - timedelta(days=random.randint(0, 180))
            ))
            
            if len(reviews) >= 100:
                Review.objects.bulk_create(reviews)
                reviews = []
        
        if reviews:
            Review.objects.bulk_create(reviews)

    @transaction.atomic
    def handle(self, *args, **kwargs):
        # Очистка существующих данных
        self.stdout.write('Очистка базы данных...')
        Review.objects.all().delete()
        Appointment.objects.all().delete()
        Client.objects.all().delete()
        Master.objects.all().delete()
        Service.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

        # Создание новых данных
        self.create_services()
        self.create_masters()
        self.create_clients()
        self.create_appointments()
        self.create_reviews()

        # Статистика
        self.stdout.write(self.style.SUCCESS(f'''
        Успешно создано:
        - {Service.objects.count()} услуг
        - {Master.objects.count()} мастеров
        - {Client.objects.count()} клиентов
        - {Appointment.objects.count()} записей
        - {Review.objects.count()} отзывов
        '''))