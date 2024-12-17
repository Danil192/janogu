from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import models
from beauty_salon.models import Client, Service, Review
from django.utils import timezone
from datetime import timedelta
import random
import faker

class Command(BaseCommand):
    help = 'Generates reviews data'

    def handle(self, *args, **kwargs):
        fake = faker.Faker('ru_RU')
        
        # Проверяем наличие клиентов
        if Client.objects.count() == 0:
            self.stdout.write('Creating clients...')
            # Создаем 50 клиентов
            for i in range(50):
                user = User.objects.create_user(
                    username=f'client{i}',
                    password='password123',
                    email=fake.email()
                )
                Client.objects.create(
                    user=user,
                    name=fake.name(),
                    phone=fake.phone_number(),
                    email=user.email
                )
            self.stdout.write(self.style.SUCCESS(f'Created {Client.objects.count()} clients'))

        # Проверяем наличие услуг
        if Service.objects.count() == 0:
            self.stdout.write('Creating services...')
            services_list = [
                {'name': 'Стрижка', 'price': 1500, 'duration': 60},
                {'name': 'Окрашивание', 'price': 4000, 'duration': 120},
                {'name': 'Маникюр', 'price': 2000, 'duration': 90},
                {'name': 'Педикюр', 'price': 2500, 'duration': 90},
                {'name': 'Массаж', 'price': 3000, 'duration': 60},
            ]
            for service_data in services_list:
                Service.objects.create(**service_data)
            self.stdout.write(self.style.SUCCESS(f'Created {Service.objects.count()} services'))

        # Очищаем существующие отзывы
        Review.objects.all().delete()

        clients = Client.objects.all()
        services = Service.objects.all()

        # Добавляем отладочную информацию
        self.stdout.write(f'Found {clients.count()} clients')
        if clients.exists():
            self.stdout.write('Sample client:')
            sample_client = clients.first()
            self.stdout.write(f'- ID: {sample_client.id}')
            self.stdout.write(f'- Name: {sample_client.name}')
            self.stdout.write(f'- User: {sample_client.user}')

        self.stdout.write(f'Found {services.count()} services')
        if services.exists():
            self.stdout.write('Sample service:')
            sample_service = services.first()
            self.stdout.write(f'- ID: {sample_service.id}')
            self.stdout.write(f'- Name: {sample_service.name}')

        positive_comments = [
            'Отличный сервис!', 'Всё понравилось', 'Рекомендую', 
            'Хороший мастер', 'Приду ещё', 'Великолепно!',
            'Всё отлично', 'Супер!', 'Очень доволен(а)', 'Спасибо большое!',
            'Профессиональная работа', 'Отличный результат',
            'Мастер своего дела!', 'Превзошло все ожидания',
            'Качественно и быстро', 'Обязательно вернусь снова'
        ]
        negative_comments = [
            'Могло быть лучше', 'Не совсем то, что ожидал(а)',
            'Есть над чем поработать', 'Среднее качество',
            'Долго ждал(а)', 'Дороговато для такого качества',
            'Не очень понравился результат', 'Больше не приду'
        ]

        reviews = []
        for _ in range(1500):
            client = random.choice(clients)
            service = random.choice(services)
            
            # 80% положительных отзывов, 20% негативных
            if random.random() < 0.8:
                rating = random.randint(4, 5)
                comment = random.choice(positive_comments)
            else:
                rating = random.randint(2, 3)
                comment = random.choice(negative_comments)
            
            # Добавляем случайные детали к комментариям
            if random.random() < 0.3:  # 30% шанс добавить детали
                additional_details = [
                    f"Была у мастера {fake.name()}.",
                    f"Потратила {random.randint(30, 120)} минут.",
                    f"Атмосфера в салоне приятная.",
                    f"Записалась через сайт, очень удобно.",
                    f"Цена соответствует качеству."
                ]
                comment += " " + random.choice(additional_details)
            
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
                self.stdout.write(f'Created {len(reviews)} reviews...')
        
        if reviews:
            Review.objects.bulk_create(reviews)

        total_reviews = Review.objects.count()
        self.stdout.write(self.style.SUCCESS(f'Successfully created {total_reviews} reviews'))
        
        # Выводим статистику
        avg_rating = Review.objects.aggregate(avg_rating=models.Avg('rating'))['avg_rating']
        five_stars = Review.objects.filter(rating=5).count()
        one_star = Review.objects.filter(rating=1).count()
        
        self.stdout.write(f'''
        Statistics:
        - Average rating: {avg_rating:.2f}
        - 5-star reviews: {five_stars}
        - 1-star reviews: {one_star}
        ''')