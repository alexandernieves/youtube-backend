"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
https://docs.djangoproject.com/en/5.0/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def home_view(request):
    return HttpResponse("Hola desde la raíz /")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('base.urls')),
    path('', home_view, name='home'),
]
