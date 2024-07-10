# content/urls.py
from django.urls import path
from .views import article_detail

urlpatterns = [
    path('info/', article_detail, name='article_detail'),
]
