from django.contrib import admin
from .models import Client, Service, Master, Appointment, Review

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'phone', 'email', 'service']
    search_fields = ['name', 'phone']

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'price', 'duration', 'picture']
    search_fields = ['name']
    
@admin.register(Master)
class MasterAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'specialization']
    search_fields = ['name']
    filter_horizontal = ['services']

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'service', 'master', 'date']
    list_filter = ['date', 'service', 'master']
    search_fields = ['client__name']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'service', 'rating', 'date']
    list_filter = ['rating', 'date', 'service']
    search_fields = ['client__name', 'comment']



