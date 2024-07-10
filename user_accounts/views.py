from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from .forms import UserRegistrationForm, EmailConfirmationForm, AdvertiserProfileForm, WebmasterProfileForm
from .models import EmailConfirmation
import random
import string
from django.utils import timezone

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Деактивировать пользователя до подтверждения почты
            user.save()
            # Генерация кода подтверждения
            confirmation_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            email = user.email
            # Проверка на существование записи с данным email
            try:
                confirmation = EmailConfirmation.objects.get(email=email)
                confirmation.confirmation_code = confirmation_code
                confirmation.is_confirmed = False
                confirmation.updated_at = timezone.now()
                confirmation.save()
            except EmailConfirmation.DoesNotExist:
                EmailConfirmation.objects.create(email=email, confirmation_code=confirmation_code)
            # Отправка кода на почту (упрощенно)
            print(f"Код подтверждения для {email}: {confirmation_code}")
            return redirect('email_confirmation')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

def email_confirmation(request):
    if request.method == 'POST':
        form = EmailConfirmationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            code = form.cleaned_data['confirmation_code']
            try:
                confirmation = EmailConfirmation.objects.get(email=email, confirmation_code=code)
                if confirmation.is_confirmed:
                    form.add_error(None, 'Этот email уже подтвержден.')
                elif confirmation.is_expired():
                    form.add_error(None, 'Код подтверждения истек.')
                else:
                    user = User.objects.get(email=email)
                    user.is_active = True
                    user.save()
                    confirmation.is_confirmed = True
                    confirmation.save()
                    return redirect('choose_role')
            except EmailConfirmation.DoesNotExist:
                form.add_error(None, 'Неверный код подтверждения.')
    else:
        form = EmailConfirmationForm()
    return render(request, 'email_confirmation.html', {'form': form})

@login_required
def choose_role(request):
    return render(request, 'choose_role.html')

@login_required
def complete_advertiser_profile(request):
    if request.method == 'POST':
        form = AdvertiserProfileForm(request.POST)
        if form.is_valid():
            advertiser = form.save(commit=False)
            advertiser.user = request.user
            advertiser.save()
            return redirect('advertiser_dashboard')
    else:
        form = AdvertiserProfileForm()
    return render(request, 'complete_profile.html', {'form': form, 'role': 'рекламодатель'})

@login_required
def complete_webmaster_profile(request):
    if request.method == 'POST':
        form = WebmasterProfileForm(request.POST, request.FILES)
        if form.is_valid():
            webmaster = form.save(commit=False)
            webmaster.user = request.user
            webmaster.save()
            return redirect('webmaster_dashboard')
    else:
        form = WebmasterProfileForm()
    return render(request, 'complete_profile.html', {'form': form, 'role': 'вебмастер'})
