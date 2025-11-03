from email.policy import default

from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    
    def __str__(self):
        return self.user
    

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
