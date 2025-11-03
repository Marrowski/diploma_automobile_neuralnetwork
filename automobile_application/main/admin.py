from django.contrib import admin
from .models import *

admin.site.register([AutoNumbers, UserProfile, Category, Logo])
# Register your models here.
