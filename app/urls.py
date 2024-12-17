"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from beauty_salon.views import ShowClients, login, logout
from rest_framework import routers
from beauty_salon.api import (
    ClientViewSet, ServiceViewSet, MasterViewSet, 
    AppointmentViewSet, ReviewViewSet, UserViewSet
)
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken import views
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse

router = routers.DefaultRouter()
router.register("clients", ClientViewSet, basename="clients")
router.register("services", ServiceViewSet, basename="services")
router.register("masters", MasterViewSet, basename="masters")
router.register("appointments", AppointmentViewSet, basename="appointments")
router.register("reviews", ReviewViewSet, basename="reviews")
router.register("users", UserViewSet, basename="users")

@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({'detail': 'CSRF cookie set'})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', ShowClients.as_view()),
    path('api/', include(router.urls)),
    path('api-token-auth/', views.obtain_auth_token),
    path('api/auth/login/', login),
    path('api/auth/logout/', logout, name='logout'),
    path('api/auth/csrf/', get_csrf_token, name='csrf'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
