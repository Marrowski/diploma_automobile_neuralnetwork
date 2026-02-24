from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import UserProfile, LoadFile, PlateScan


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
    common_classes = (
        "w-full px-4 py-2.5 rounded-xl border border-gray-300 bg-white text-gray-900 "
        "focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 focus:outline-none transition-all "
        "dark:bg-slate-900 dark:border-slate-700 dark:text-white dark:placeholder-slate-500 "
        "dark:focus:border-blue-500"
    )

    name = forms.CharField(
        max_length=150,
        required=False,
        label="Ім'я",
        widget=forms.TextInput(attrs={
            "class": common_classes,
            "placeholder": "Ваше ім'я"
        }),
    )

    password = forms.CharField(
        required=False,
        label="Новий пароль",
        widget=forms.PasswordInput(attrs={
            "class": common_classes,
            "placeholder": "••••••••"
        }),
    )

    confirm_password = forms.CharField(
        required=False,
        label="Підтвердити пароль",
        widget=forms.PasswordInput(attrs={
            "class": common_classes,
            "placeholder": "••••••••"
        }),
    )

    class Meta:
        model = UserProfile
        fields = ["avatar"]
        widgets = {"avatar": AvatarInput(attrs={"class": file_input_class, "accept": "image/*"})}
        labels = {"avatar": "Змінити аватар"}

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields["name"].initial = self.user.first_name

    def clean(self):
        cleaned = super().clean()
        pwd = cleaned.get("password")
        confirm = cleaned.get("confirm_password")
        if pwd or confirm:
            if pwd != confirm:
                raise forms.ValidationError("Паролі не збігаються")
            if len(pwd) < 8:
                raise forms.ValidationError("Пароль має бути не менше 8 символів")
        return cleaned

    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.user:
            name = self.cleaned_data.get("name")
            pwd = self.cleaned_data.get("password")
            if name is not None:
                self.user.first_name = name
            if pwd:
                self.user.set_password(pwd)
            if commit:
                self.user.save()
                profile.save()
        return profile

class LoadFileForm(forms.ModelForm):
    class Meta:
        model = LoadFile
        fields = ["name_file", "auto_file"]
        widgets = {
            "auto_file": forms.ClearableFileInput(attrs={
                "class": "hidden",
                "accept": "image/*,video/*"
            })
        }
        labels = {
            "auto_file": "Файл (фото/відео)"
        }


class ANPRUploadForm(forms.Form):
    file = forms.FileField(
        label="Фото або відео",
        help_text="Підтримка: JPG/PNG/JPEG, MP4/MOV/AVI",
        widget=forms.ClearableFileInput(attrs={"accept": "image/*,video/*"})
    )