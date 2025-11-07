from .models import UserProfile


def user_profile_picture(request):
    prof_pic = None

    if request.user.is_authenticated:
        prof_pic = UserProfile.objects.filter(user=request.user).first()

    return {'prof_pic': prof_pic}