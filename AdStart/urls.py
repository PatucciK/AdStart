# AdStart/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('user_accounts.urls')),
    path('content/', include('content.urls')),
    path('partner_cards/', include('partner_cards.urls')),
    path('offers/', include('offers.urls')),
]
