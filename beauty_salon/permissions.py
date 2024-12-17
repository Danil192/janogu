from rest_framework.permissions import BasePermission
from django.core.cache import cache

class OTPRequired(BasePermission):
    def has_permission(self, request, view):
        # Разрешаем GET запросы без OTP
        if request.method in ['GET']:
            return True
            
        # Для PUT/DELETE требуем OTP
        if request.method in ['PUT', 'DELETE']:
            otp_key = cache.get(f'otp_good_{request.user.id}', False)
            return bool(request.user and otp_key)
            
        return True