from django.urls import path
from .views import AdvertiserOffersView

urlpatterns = [
    path('advertiser_offers/', AdvertiserOffersView.as_view(), name='advertiser_offers'),
]