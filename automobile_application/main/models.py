from email.policy import default

from django.db import models
from django.contrib.auth.models import User

from django.contrib.postgres.fields import ArrayField
from django.contrib.auth import get_user_model


class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    avatar = models.ImageField('Аватар', upload_to='avatars/', default='avatars/user.png', blank=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f'Профіль {self.user.username}'
    

class AutoNumbers(models.Model):
    user = models.ForeignKey(User, verbose_name='Користувач', on_delete=models.CASCADE, related_name='numbers_user')
    numbers = models.CharField(max_length=8)
    is_allowed = models.BooleanField()
    time_create = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.numbers


class Category(models.Model):
    user = models.ForeignKey(User, verbose_name='Користувач', on_delete=models.CASCADE, related_name='category_user')
    numbers = models.ManyToManyField(AutoNumbers, related_name='category_numbers')
    choice = [('Ukraine', 'Україна'), ('Europe', 'ЄС'), ('USA', 'США'), ('Japan', 'Japan')]

    category = models.CharField(max_length=50, choices=choice, default=None)


    def __str__(self):
        return self.category


class Logo(models.Model):
    logo = models.ImageField()


class LoadFile(models.Model):
    name_file = models.CharField(max_length=100)
    auto_file = models.FileField()

class PlateScan(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name= models.CharField(max_length=120)
    image = models.ImageField(upload_to="scans/images/", blank=True, null=True)
    video = models.FileField(upload_to="scans/videos/", blank=True, null=True)
    plate_texts = ArrayField(models.CharField(max_length=16), default=list, blank=True)
    is_ukrainian = models.BooleanField(default=False)
    raw_bboxes = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        src = 'video' if self.video else 'image'
        return f'{self.id}:{src}:{self.name or ''}'