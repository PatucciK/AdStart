import random
import string
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from asgiref.sync import sync_to_async
from .forms import AdvertiserRegistrationForm, WebmasterRegistrationForm
from .models import Advertiser, Webmaster, EmailConfirmation

async def register(request):
    return render(request, 'user_accounts/register.html')

async def register_webmaster(request):
    if request.method == 'POST':
        form = WebmasterRegistrationForm(request.POST, request.FILES)
        if await sync_to_async(form.is_valid)():
            webmaster = form.save(commit=False)
            webmaster.password = make_password(form.cleaned_data['password'])

            # Создание или обновление записи подтверждения email
            confirmation_code = ''.join(random.choices(string.digits, k=6))
            email_confirmation, created = await sync_to_async(EmailConfirmation.objects.update_or_create)(
                email=webmaster.email,
                defaults={'confirmation_code': confirmation_code, 'is_confirmed': False}
            )

            # Сохранение данных вебмастера в сессии
            session_data = {
                'email': webmaster.email,
                'telegram': webmaster.telegram,
                'phone': webmaster.phone,
                'password': webmaster.password,
                'experience': webmaster.experience,
                'stats_screenshot': webmaster.stats_screenshot.name,
            }
            await sync_to_async(request.session.__setitem__)('webmaster_data', session_data)

            # Отправка email с кодом подтверждения (асинхронно)
            await sync_to_async(send_mail)(
                'Подтверждение email',
                f'Ваш код подтверждения: {confirmation_code}',
                'from@example.com',  # замените на ваш email
                [webmaster.email],
                fail_silently=False,
            )
            return redirect('confirm_email_webmaster', email=webmaster.email)  # Замените на нужный URL
    else:
        form = WebmasterRegistrationForm()
    return render(request, 'user_accounts/register_webmaster.html', {'form': form})

async def register_advertiser(request):
    if request.method == 'POST':
        form = AdvertiserRegistrationForm(request.POST)
        if await sync_to_async(form.is_valid)():
            advertiser = form.save(commit=False)
            advertiser.password = make_password(form.cleaned_data['password'])

            # Создание или обновление записи подтверждения email
            confirmation_code = ''.join(random.choices(string.digits, k=6))
            email_confirmation, created = await sync_to_async(EmailConfirmation.objects.update_or_create)(
                email=advertiser.email,
                defaults={'confirmation_code': confirmation_code, 'is_confirmed': False}
            )

            # Сохранение данных рекламодателя в сессии
            session_data = {
                'email': advertiser.email,
                'telegram': advertiser.telegram,
                'phone': advertiser.phone,
                'password': advertiser.password,
            }
            await sync_to_async(request.session.__setitem__)('advertiser_data', session_data)

            # Отправка email с кодом подтверждения (асинхронно)
            await sync_to_async(send_mail)(
                'Подтверждение email',
                f'Ваш код подтверждения: {confirmation_code}',
                'from@example.com',  # замените на ваш email
                [advertiser.email],
                fail_silently=False,
            )
            return redirect('confirm_email', email=advertiser.email)  # Замените на нужный URL
    else:
        form = AdvertiserRegistrationForm()
    return render(request, 'user_accounts/register_advertiser.html', {'form': form})

async def confirm_email(request, email):
    email_confirmation = await sync_to_async(EmailConfirmation.objects.get)(email=email)
    if request.method == 'POST':
        code = request.POST.get('code')
        if code == email_confirmation.confirmation_code:
            email_confirmation.is_confirmed = True
            await sync_to_async(email_confirmation.save)()

            # Извлечение данных рекламодателя из сессии и создание записи в таблице Advertiser
            advertiser_data = await sync_to_async(request.session.__getitem__)('advertiser_data')
            if advertiser_data:
                hashed_password = make_password(advertiser_data['password'])
                await sync_to_async(Advertiser.objects.create)(
                    email=advertiser_data['email'],
                    telegram=advertiser_data['telegram'],
                    phone=advertiser_data['phone'],
                    password=hashed_password,
                )
                await sync_to_async(request.session.__delitem__)('advertiser_data')  # Очистка данных из сессии

            return redirect('login')  # Замените на нужный URL
        else:
            return render(request, 'user_accounts/confirm_email.html', {'error': 'Неправильный код', 'email': email})
    return render(request, 'user_accounts/confirm_email.html', {'email': email})

async def confirm_email_webmaster(request, email):
    email_confirmation = await sync_to_async(EmailConfirmation.objects.get)(email=email)
    if request.method == 'POST':
        code = request.POST.get('code')
        if code == email_confirmation.confirmation_code:
            email_confirmation.is_confirmed = True
            await sync_to_async(email_confirmation.save)()

            # Извлечение данных вебмастера из сессии и создание записи в таблице Webmaster
            webmaster_data = await sync_to_async(request.session.__getitem__)('webmaster_data')
            if webmaster_data:
                hashed_password = make_password(webmaster_data['password'])
                await sync_to_async(Webmaster.objects.create)(
                    email=webmaster_data['email'],
                    telegram=webmaster_data['telegram'],
                    phone=webmaster_data['phone'],
                    password=hashed_password,
                    experience=webmaster_data['experience'],
                    stats_screenshot=webmaster_data['stats_screenshot'],
                )
                await sync_to_async(request.session.__delitem__)('webmaster_data')  # Очистка данных из сессии

            return redirect('login')  # Замените на нужный URL
        else:
            return render(request, 'user_accounts/confirm_email_webmaster.html', {'error': 'Неправильный код', 'email': email})
    return render(request, 'user_accounts/confirm_email_webmaster.html', {'email': email})
