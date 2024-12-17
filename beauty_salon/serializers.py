from rest_framework import serializers
from .models import Client, Service, Master, Appointment, Review
from django.utils import timezone

class BaseModelSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        if 'user' in validated_data:
            validated_data.pop('user')
        return super().create(validated_data)

class ServiceSerializer(BaseModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'name', 'price', 'duration', 'picture']
        read_only_fields = ['id']

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'name', 'phone', 'email', 'service', 'picture', 'user']
        read_only_fields = ['id', 'user']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user:
            validated_data['user'] = request.user
            return super().create(validated_data)

class MasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Master
        fields = ['id', 'name', 'specialization', 'services']
        read_only_fields = ['id']

    def create(self, validated_data):
        services = validated_data.pop('services', [])
        master = Master.objects.create(**validated_data)
        master.services.set(services)
        return master

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['id', 'client', 'service', 'master', 'date']
        read_only_fields = ['id', 'client']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user:
            try:
                client = Client.objects.filter(user=request.user).first()
                if not client:
                    raise serializers.ValidationError("Client profile not found for current user")
                validated_data['client'] = client
                return super().create(validated_data)
            except Exception as e:
                raise serializers.ValidationError(str(e))

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'client', 'service', 'rating', 'comment', 'date']
        read_only_fields = ['id', 'client', 'date']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user:
            try:
                client = Client.objects.filter(user=request.user).first()
                if not client:
                    raise serializers.ValidationError("Client profile not found for current user")
                validated_data['client'] = client
                validated_data['date'] = timezone.now()
                return super().create(validated_data)
            except Exception as e:
                raise serializers.ValidationError(str(e))
