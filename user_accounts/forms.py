from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Advertiser, Webmaster

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class EmailConfirmationForm(forms.Form):
    email = forms.EmailField(required=True)
    confirmation_code = forms.CharField(max_length=6, required=True)

class AdvertiserProfileForm(forms.ModelForm):
    class Meta:
        model = Advertiser
        fields = ['telegram', 'phone']

class WebmasterProfileForm(forms.ModelForm):
    class Meta:
        model = Webmaster
        fields = ['telegram', 'phone', 'experience', 'stats_screenshot']
