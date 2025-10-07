from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.forms import model_to_dict

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
    # user = User.objects.filter(user=request.user)
    url = 'https://russianwarship.rip/api/v1/statistics?offset=50&limit=1'
    
    try:
        response = requests.get(url, timeout=5)
        data_json = response.json()

        record = data_json['data']['records'][0]
        stats = record['stats']

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
        'atgm': atgm
    }
    
    return render(request, 'base.html', context)


class AutoNumbersAPIList(generics.ListCreateAPIView):
    queryset = AutoNumbers.objects.all()
    serializer_class = AutoNumbersSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )


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


class CategoryAPIUpdate(generics.RetrieveUpdateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticated, )
    # authentication_classes = (TokenAuthentication, )


class CategoryAPIDestroy(generics.RetrieveDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)