from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import UserProfile

text_input_class = (
    "mt-1 block w-full rounded-md border-gray-300 shadow-sm "
    "focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
)
file_input_class = (
    "mt-1 block w-full text-sm text-gray-900 border border-gray-300 rounded-lg "
    "cursor-pointer bg-gray-50 focus:outline-none "
    "file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 "
    "file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 "
    "hover:file:bg-indigo-100"
)

class AvatarInput(forms.ClearableFileInput):
    template_name = "django/forms/widgets/input.html"
    initial_text = ""
    input_text = ""
    clear_checkbox_label = ""

class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={
            "class": text_input_class, "placeholder": "••••••••", "autocomplete": "new-password", "maxlength": "14"
        })
    )
    password2 = forms.CharField(
        label="Повторіть пароль",
        widget=forms.PasswordInput(attrs={
            "class": text_input_class, "placeholder": "••••••••", "autocomplete": "new-password", "maxlength": "14"
        })
    )
    profile_picture = forms.ImageField(
        label="Фото профілю (необов'язково)",
        required=False,
        widget=AvatarInput(attrs={"class": file_input_class, "accept": "image/*"})
    )

    class Meta:
        model = User
        fields = ("username", "first_name", "email")
        widgets = {
            "username": forms.TextInput(attrs={"class": text_input_class, "placeholder": "Ваш унікальний логін", "autocomplete": "username"}),
            "first_name": forms.TextInput(attrs={"class": text_input_class, "placeholder": "Ваше ім'я", "autocomplete": "given-name"}),
            "email": forms.EmailInput(attrs={"class": text_input_class, "placeholder": "example@mail.com", "autocomplete": "email"}),
        }
        labels = {"username": "Логін", "first_name": "Ім'я", "email": "Email"}
        help_texts = {"username": ""}

    def clean(self):
        cleaned = super().clean()
        p1, p2 = cleaned.get("password"), cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            raise ValidationError("Паролі не співпадають.")
        if p1 and len(p1) < 8:
            raise ValidationError("Пароль має містити щонайменше 8 символів.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            avatar = self.cleaned_data.get("profile_picture")
            if avatar is not None:
                UserProfile.objects.update_or_create(user=user, defaults={"avatar": avatar})
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["avatar"]
        widgets = {"avatar": AvatarInput(attrs={"class": file_input_class, "accept": "image/*"})}
        labels = {"avatar": "Змінити аватар"}
