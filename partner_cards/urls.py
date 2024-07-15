# partner_cards/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('edit/', views.edit_partner_card, name='edit_partner_card'),
    path('view/', views.view_partner_card, name='view_partner_card'),
]
