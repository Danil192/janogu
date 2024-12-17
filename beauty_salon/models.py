from django.db import models
from django.contrib.auth.models import User

class Service(models.Model):
    name = models.TextField("Название услуги")
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    duration = models.IntegerField("Длительность (мин)")
    picture = models.ImageField("Изображение", null=True, upload_to="services")

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"

    def __str__(self):
        return self.name

class Client(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True)
    picture = models.ImageField(upload_to='clients/', null=True, blank=True)

    def __str__(self):
        return self.name

class Master(models.Model):
    name = models.TextField("ФИО мастера")
    specialization = models.TextField("Специализация")
    services = models.ManyToManyField(Service, related_name="masters")

    class Meta:
        verbose_name = "Мастер"
        verbose_name_plural = "Мастера"

    def __str__(self):
        return self.name

class Appointment(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    master = models.ForeignKey(Master, on_delete=models.CASCADE)
    date = models.DateTimeField("Дата и время")

    class Meta:
        verbose_name = "Запись"
        verbose_name_plural = "Записи"

    def __str__(self):
        return f"{self.client} - {self.service} - {self.date}"

class Review(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    rating = models.IntegerField("Оценка", choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField("Комментарий")
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def __str__(self):
        return f"{self.client} - {self.service} - {self.rating}"
