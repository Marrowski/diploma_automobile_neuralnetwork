"""
URL configuration for automobile_application project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include, re_path
from main.views import *
from django.conf.urls.static import static
from django.conf import settings

from rest_framework import routers



urlpatterns = [
    path('admin/', admin.site.urls),
    path("__reload__/", include("django_browser_reload.urls")),
    path('', main_view, name='base'),
    path('api/v1/numbers/', AutoNumbersAPIList.as_view()),
    path('api/v1/numbers/<int:pk>/', AutoNumbersAPIUpdate.as_view()),
    path('api/v1/numbersdelete/<int:pk>/', AutoNumbersAPIDestroy.as_view()),
    path('api/v1/category/', CategoryAPIList.as_view()),
    path('api/v1/category/<int:pk>/', CategoryAPIUpdate.as_view()),
    path('api/v1/categorydelete/<int:pk>/', CategoryAPIDestroy.as_view()),
    path('api/v1/drf-auth/', include('rest_framework.urls')),
    path('api/v1/auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
    path('register/', register_view, name='register'),
    path('profile/', user_profile, name='profile')
]

if settings.DEBUG:
    urlpatterns +=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)