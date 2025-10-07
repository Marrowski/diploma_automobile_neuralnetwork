from django.contrib import admin
from .models import *

admin.site.register([AutoNumbers, UserProfile, Category])
# Register your models here.
