from django import forms
from django.contrib.auth.models import User

class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(help_text='Пароль', max_length=14)
    password2 = forms.CharField(help_text='Повторіть пароль', max_length=14)
    profile_picture = forms.ImageField()

    class Meta:
        model = User
        fields = ('username', 'first_name', 'email')