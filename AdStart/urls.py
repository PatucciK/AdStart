# AdStart/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('user_accounts.urls')),
    path('content/', include('content.urls')),
]
