from django.urls import path
from .views import (
    AdvertiserOffersView,
    CreateOfferView,
    OfferDetailView,
    DeleteOfferView,
    PauseOfferView,
    UnpauseOfferView,
    AvailableOffersView,
    MyOffersView,
    take_offer,
    WebmasterOfferDetailView,
    WebmasterLeadsView,
    WebmasterOfferStatisticsView,
    WebmasterFinancialStatisticsView,
    AdvertiserOfferStatisticsView,
    AdvertiserFinancialStatisticsView,
    AdvertiserLeadsView,
)

urlpatterns = [
    path('advertiser_offers/', AdvertiserOffersView.as_view(), name='advertiser_offers'),
    path('create_offer/', CreateOfferView.as_view(), name='create_offer'),
    path('offer/<int:pk>/', OfferDetailView.as_view(), name='offer_detail'),
    path('delete_offer/<int:pk>/', DeleteOfferView.as_view(), name='delete_offer'),
    path('pause_offer/<int:pk>/', PauseOfferView.as_view(), name='pause_offer'),
    path('unpause_offer/<int:pk>/', UnpauseOfferView.as_view(), name='unpause_offer'),
    path('webmaster/statistics/offers/', WebmasterOfferStatisticsView.as_view(), name='webmaster_offer_statistics'),
    path('webmaster/statistics/financial/', WebmasterFinancialStatisticsView.as_view(), name='webmaster_financial_statistics'),
]

urlpatterns += [
    path('available_offers/', AvailableOffersView.as_view(), name='available_offers'),
    path('my_offers/', MyOffersView.as_view(), name='my_offers'),
    path('take_offer/<int:offer_id>/', take_offer, name='take_offer'),
    path('webmaster/<int:pk>/', WebmasterOfferDetailView.as_view(), name='webmaster_offer_detail'),
    path('webmaster/leads/', WebmasterLeadsView.as_view(), name='webmaster_leads'),
    path('advertiser/statistics/offers/', AdvertiserOfferStatisticsView.as_view(), name='advertiser_offer_statistics'),
    path('advertiser/statistics/financial/', AdvertiserFinancialStatisticsView.as_view(), name='advertiser_financial_statistics'),
    path('advertiser/leads/', AdvertiserLeadsView.as_view(), name='advertiser_leads'),
]
