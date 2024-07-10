# urls.py
from django.urls import path
from .views import register, email_confirmation, choose_role, complete_advertiser_profile, complete_webmaster_profile

urlpatterns = [
    path('register/', register, name='register'),
    path('email_confirmation/', email_confirmation, name='email_confirmation'),
    path('choose_role/', choose_role, name='choose_role'),
    path('complete_advertiser_profile/', complete_advertiser_profile, name='complete_advertiser_profile'),
    path('complete_webmaster_profile/', complete_webmaster_profile, name='complete_webmaster_profile'),
]
