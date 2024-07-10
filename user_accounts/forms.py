from django import forms
from .models import Advertiser, Webmaster


class AdvertiserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')
    password_confirm = forms.CharField(widget=forms.PasswordInput, label='Подтвердите пароль')

    class Meta:
        model = Advertiser
        fields = ['email', 'telegram', 'phone']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        telegram = cleaned_data.get("telegram")
        phone = cleaned_data.get("phone")

        if password and password != password_confirm:
            raise forms.ValidationError("Пароли не совпадают")

        if not telegram and not phone:
            raise forms.ValidationError("Пожалуйста, укажите ваш Telegram или телефон")

        if phone and (not phone.isdigit() or len(phone) != 10):
            raise forms.ValidationError("Номер телефона должен содержать 10 цифр")

        return cleaned_data


class WebmasterRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')
    password_confirm = forms.CharField(widget=forms.PasswordInput, label='Подтвердите пароль')

    class Meta:
        model = Webmaster
        fields = ['email', 'telegram', 'phone', 'experience', 'stats_screenshot']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password != password_confirm:
            raise forms.ValidationError("Пароли не совпадают")

        return cleaned_data
