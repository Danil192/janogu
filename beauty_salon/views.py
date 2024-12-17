from typing import Any
from django.shortcuts import render
from django.http import HttpResponse
from beauty_salon.models import Client
from django.views.generic import TemplateView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from django.views.decorators.csrf import ensure_csrf_cookie

class ShowClients(TemplateView):
    template_name = 'clients/show_clients.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['clients'] = Client.objects.all()
        return context

@api_view(['POST'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    print(f"Login attempt for {username}")
    print(f"Request data: {request.data}")
    
    try:
        user = User.objects.get(username=username)
        print(f"Found user: {user.username}")
        print(f"User active: {user.is_active}")
        print(f"User staff: {user.is_staff}")
        print(f"User superuser: {user.is_superuser}")
    except User.DoesNotExist:
        print(f"User {username} not found")
        return Response({'error': 'Invalid credentials'}, status=400)
    
    auth_user = authenticate(username=username, password=password)
    print(f"Authentication result: {auth_user}")
    
    if auth_user:
        token, _ = Token.objects.get_or_create(user=auth_user)
        print(f"Generated token: {token.key}")
        return Response({
            'token': token.key,
            'user_id': auth_user.pk,
            'username': auth_user.username
        })
    
    print("Authentication failed")
    return Response({'error': 'Invalid credentials'}, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        print(f"Logout attempt for user: {request.user.username}")  # Для отладки
        if hasattr(request.user, 'auth_token'):
            print(f"Deleting token: {request.user.auth_token.key}")  # Для отладки
            request.user.auth_token.delete()
            return Response({'message': 'Successfully logged out'})
        return Response({'message': 'No token found'})
    except Exception as e:
        print(f"Logout error: {str(e)}")  # Для отладки
        return Response({'error': str(e)}, status=400)

