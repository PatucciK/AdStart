# user_accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Advertiser, Webmaster


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }


class EmailConfirmationForm(forms.Form):
    confirmation_code = forms.CharField(max_length=6, required=True,
                                        widget=forms.TextInput(attrs={'class': 'form-control'}))


class AdvertiserProfileForm(forms.ModelForm):
    class Meta:
        model = Advertiser
        fields = ['telegram', 'phone']
        widgets = {
            'telegram': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }


class WebmasterProfileForm(forms.ModelForm):
    class Meta:
        model = Webmaster
        fields = ['telegram', 'phone', 'experience', 'stats_screenshot']
        widgets = {
            'telegram': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'experience': forms.Textarea(attrs={'class': 'form-control'}),
            'stats_screenshot': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
