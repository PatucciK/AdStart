# AdStart/urls.py
from django.contrib import admin
from django.urls import path, include
from user_accounts import views as user_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/register/', user_views.register, name='register'),
    path('accounts/email_confirmation/', user_views.email_confirmation, name='email_confirmation'),
    path('accounts/choose_role/', user_views.choose_role, name='choose_role'),
    path('accounts/complete_advertiser_profile/', user_views.complete_advertiser_profile, name='complete_advertiser_profile'),
    path('accounts/complete_webmaster_profile/', user_views.complete_webmaster_profile, name='complete_webmaster_profile'),
    path('accounts/', include('django.contrib.auth.urls')),  # Стандартные URL-адреса для аутентификации
]
