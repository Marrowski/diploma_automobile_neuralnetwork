from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.forms import model_to_dict
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from rest_framework.pagination import PageNumberPagination
from rest_framework.authentication import TokenAuthentication
from rest_framework import generics, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly, IsAuthenticated
from .permissions import *

from .models import *
from .forms import *
from .serializers import *

import requests


def main_view(request):
    url = 'https://russianwarship.rip/api/v2/statistics/latest/'
    logo = Logo.objects.all()
    prof_pic = None

    if request.user.is_authenticated:
        prof_pic = UserProfile.objects.filter(user=request.user).first()

    
    try:
        response = requests.get(url, timeout=5)
        data_json = response.json()

        stats = data_json['data']['stats']

        units = stats['personnel_units']
        tanks = stats['tanks']
        afv = stats['armoured_fighting_vehicles']
        art = stats['artillery_systems']
        mlrs = stats['mlrs']
        aaws = stats['aa_warfare_systems']
        planes = stats['planes']
        heli = stats['helicopters']
        vft = stats['vehicles_fuel_tanks']
        wcut = stats['warships_cutters']
        cm = stats['cruise_missiles']
        uav = stats['uav_systems']
        sme = stats['special_military_equip']
        submarines = stats['submarines']
        atgm = stats['atgm_srbm_systems']
    
    except requests.exceptions.RequestException as e:
        return render('theme/base.html', {'error': f'Помилка запиту:{e}.'})
    except requests.exceptions.Timeout:
        return render('theme/base.html', {'error': 'Час очікування сплив.'})
    
    context = {
        'units':units,
        'tanks':tanks,
        'afv':afv,
        'art':art,
        'mlrs':mlrs,
        'aaws':aaws,
        'planes':planes,
        'heli':heli,
        'vft':vft,
        'wcut':wcut,
        'cm':cm,
        'uav':uav,
        'sme':sme,
        'subm':submarines,
        'atgm': atgm,
        'logo': logo,
        'prof_pic': prof_pic
    }
    
    return render(request, 'base.html', context)


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            new_user = form.save()
            login(request, new_user)
            messages.success(request, "Реєстрація успішна!")
            return redirect("base")
        messages.error(request, "Перевірте правильність заповнення форми.")
    else:
        form = RegisterForm()

    context = {
        'form': form
    }

    return render(request, "register.html", context)


@login_required
def user_profile(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Профіль оновлено.")
            return redirect("profile")
        messages.error(request, "Перевірте поля форми.")
    else:
        form = UserProfileForm(instance=profile)

    context = {
        'form': form
    }
    return render(request, "profile.html", context)


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Вхід успішний!')
            return redirect('base')
        else:
            messages.error(request, 'Невірний логін або пароль')

    return render(request, 'login.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('base')



class AutoNumbersAPIListPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100


class CategoryAPIListPagination(PageNumberPagination):
    page_size = 2
    page_size_query_param = 'page_size'
    max_page_size = 100


class AutoNumbersAPIList(generics.ListCreateAPIView):
    queryset = AutoNumbers.objects.all()
    serializer_class = AutoNumbersSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
    pagination_class = AutoNumbersAPIListPagination


class AutoNumbersAPIUpdate(generics.RetrieveUpdateAPIView):
    queryset = AutoNumbers.objects.all()
    serializer_class = AutoNumbersSerializer
    permission_classes = (IsAuthenticated, )
    # authentication_classes = (TokenAuthentication, )


class AutoNumbersAPIDestroy(generics.RetrieveDestroyAPIView):
    queryset = AutoNumbers.objects.all()
    serializer_class = AutoNumbersSerializer
    permission_classes = (IsAdminOrReadOnly, )


class CategoryAPIList(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = CategoryAPIListPagination


class CategoryAPIUpdate(generics.RetrieveUpdateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticated, )
    # authentication_classes = (TokenAuthentication, )


class CategoryAPIDestroy(generics.RetrieveDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)