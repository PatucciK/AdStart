# user_accounts/views.py
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, logout, authenticate, login
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .forms import UserRegistrationForm, EmailConfirmationForm, AdvertiserProfileForm, WebmasterProfileForm
from .models import EmailConfirmation, Advertiser, Webmaster
import random
import string
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from partner_cards.models import PartnerCard

User = get_user_model()


@method_decorator(csrf_exempt, name='dispatch')
class CustomLoginView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'registration/login.html')

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return JsonResponse({"success": True}, status=200)
        else:
            return JsonResponse({"success": False, "error": "Неверное имя пользователя или пароль."}, status=401)


def register(request):

    from AdStart.celery import  send_verification_email_async

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
            # Отправка кода на почту
            # send_verification_email_async(email, confirmation_code)
            print(confirmation_code)
            request.session['email'] = email
            return redirect('email_confirmation')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})


def email_confirmation(request):
    email = request.session.get('email')
    if not email:
        return redirect('register')

    if request.method == 'POST':
        form = EmailConfirmationForm(request.POST)
        if form.is_valid():
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
    return render(request, 'email_confirmation.html', {'form': form, 'email': email})


@login_required
def choose_role(request):
    if Advertiser.objects.filter(user=request.user).exists() or Webmaster.objects.filter(user=request.user).exists():
        return redirect('profile')
    return render(request, 'choose_role.html')


@login_required
def complete_advertiser_profile(request):
    if request.method == 'POST':
        form = AdvertiserProfileForm(request.POST)
        if form.is_valid():
            advertiser = form.save(commit=False)
            advertiser.user = request.user
            advertiser.save()
            return redirect('profile')
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
            return redirect('profile')
    else:
        form = WebmasterProfileForm()
    return render(request, 'complete_profile.html', {'form': form, 'role': 'вебмастер'})


@login_required
def profile(request):
    user = request.user
    advertiser_profile = None
    webmaster_profile = None

    try:
        advertiser_profile = Advertiser.objects.get(user=user)
    except Advertiser.DoesNotExist:
        pass

    try:
        webmaster_profile = Webmaster.objects.get(user=user)
    except Webmaster.DoesNotExist:
        pass

    context = {
        'user': user,
        'advertiser_profile': advertiser_profile,
        'webmaster_profile': webmaster_profile,
    }
    return render(request, 'profile.html', context)


def custom_logout(request):
    logout(request)
    return redirect('login')
