from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    
    def __str__(self):
        return self.user
    

class AutoNumbers(models.Model):
    numbers = models.CharField(max_length=8)
    is_allowed = models.BooleanField()
    time_create = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.numbers
