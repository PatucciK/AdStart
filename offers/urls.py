from django.urls import path
from .views import (
    AdvertiserOffersView,
    CreateOfferView,
    OfferDetailView,
    DeleteOfferView,
    PauseOfferView,
    UnpauseOfferView, AvailableOffersView, MyOffersView, take_offer, WebmasterOfferDetailView
)

urlpatterns = [
    path('advertiser_offers/', AdvertiserOffersView.as_view(), name='advertiser_offers'),
    path('create_offer/', CreateOfferView.as_view(), name='create_offer'),
    path('offer/<int:pk>/', OfferDetailView.as_view(), name='offer_detail'),
    path('delete_offer/<int:pk>/', DeleteOfferView.as_view(), name='delete_offer'),
    path('pause_offer/<int:pk>/', PauseOfferView.as_view(), name='pause_offer'),
    path('unpause_offer/<int:pk>/', UnpauseOfferView.as_view(), name='unpause_offer'),
]

urlpatterns += [
    path('available_offers/', AvailableOffersView.as_view(), name='available_offers'),
    path('my_offers/', MyOffersView.as_view(), name='my_offers'),
    path('take_offer/<int:offer_id>/', take_offer, name='take_offer'),
    path('webmaster/<int:pk>/', WebmasterOfferDetailView.as_view(), name='webmaster_offer_detail'),
]
