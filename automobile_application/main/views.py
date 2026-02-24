from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.forms import model_to_dict
from django.core.files.base import ContentFile
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings

from .models import *
from .forms import *

import requests
import os

from .forms import ANPRUploadForm
from .models import PlateScan
from django.core.files.storage import default_storage
import mimetypes
from anpr.detector import anpr_infer_image_path, anpr_infer_video_path

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


def load_file(request):
    files = LoadFile.objects.order_by("-id")
    if request.method == 'POST':
        form = LoadFileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success('Файла успішно завантажено!')
            return redirect('load')
        else:
            return messages.error('Перевірте правильність файлу.')
    else:
        form = LoadFileForm()

        context = {
            'form': form,
            'files': files
        }

    return render(request, 'anpr_upload.html', context)


def anpr_upload(request):
    if request.method == "POST":
        form = ANPRUploadForm(request.POST, request.FILES)
        if form.is_valid():
            f = form.cleaned_data["file"]

            name = default_storage.save(f"anpr_uploads/{f.name}", ContentFile(f.read()))
            path = default_storage.path(name)

            ctype, _ = mimetypes.guess_type(f.name)
            is_image = (ctype or "").startswith("image/")
            is_video = (ctype or "").startswith("video/")

            try:
                if is_image:
                    result = anpr_infer_image_path(path)
                elif is_video:
                    result = anpr_infer_video_path(path)
                else:
                    messages.error(request, "Невідомий тип файлу. Завантажте фото або відео.")
                    return redirect("anpr_upload")
            except Exception as e:
                messages.error(request, f"Помилка під час обробки: {e}")
                return redirect("anpr_upload")

            if "error" in result:
                messages.error(request, result["error"])
                return redirect("anpr_upload")

            accepted = bool(result.get("accepted"))
            plates = result.get("plates", [])

            normalized = []
            for p in plates:
                if isinstance(p, dict):
                    normalized.append({
                        "text": p.get("text", ""),
                        "is_ua": bool(p.get("is_ua")),
                        "score": p.get("score"),
                    })
                else:
                    normalized.append({"text": str(p), "is_ua": None, "score": None})

            if request.user.is_authenticated:
                plate_texts = [p["text"] for p in normalized if p["text"]]
                raw_bboxes = [p.get("bbox", []) for p in result.get("plates", []) if isinstance(p, dict)]

                scan = PlateScan(
                    owner=request.user,
                    name=f.name,
                    plate_texts=plate_texts,
                    is_ukrainian=accepted,
                    raw_bboxes=raw_bboxes,
                )

                if is_image:
                    scan.image.name = name
                elif is_video:
                    scan.video.name = name

                scan.save()

                for p in normalized:
                    if p["text"]:
                        AutoNumbers.objects.create(
                            user=request.user,
                            numbers=p["text"][:8],
                            is_allowed=bool(p.get("is_ua")),
                        )

            context = {
                "form": ANPRUploadForm(),
                "uploaded_rel": name,
                "is_image": is_image,
                "is_video": is_video,
                "accepted": accepted,
                "plates": normalized,
            }
            return render(request, "anpr_upload.html", context)

    else:
        form = ANPRUploadForm()

    return render(request, "anpr_upload.html", {"form": form})
