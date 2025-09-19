from django import forms

class RegisterForm(forms.Form):
    nickname = forms.CharField(required=True, help_text='Ім`я користувача', max_length=14)
    email = forms.EmailField(required=True, help_text='Ваш Email', max_length=26)
    password1 = forms.CharField(required=True, help_text='Пароль', max_length=14)
    password2 = forms.CharField(required=True, help_text='Повторіть ваш пароль', max_length=14)
    

class LoginForm(forms.Form):
    nickname = forms.CharField(required=True, help_text='Ім`я користувача')
    password = forms.CharField(required=True, help_text='Пароль')