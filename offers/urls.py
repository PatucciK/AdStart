from django.urls import path

from partner_cards.views import AddMetrikaTokenView
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
    remove_offer,
    WebmasterOfferDetailView,
    WebmasterLeadsView,
    WebmasterOfferStatisticsView,
    WebmasterFinancialStatisticsView,
    AdvertiserOfferStatisticsView,
    AdminOfferStatisticsView,
    AdvertiserFinancialStatisticsView,
    AdvertiserLeadsView,
    WebmasterClicksView,
    add_comment,
    download_offer_archive, WebmasterTrashLeadsView,
)

urlpatterns = [
    path('advertiser_offers/', AdvertiserOffersView.as_view(), name='advertiser_offers'),
    path('create_offer/', CreateOfferView.as_view(), name='create_offer'),
    path('offer/<int:pk>/', OfferDetailView.as_view(), name='offer_detail'),
    path('delete_offer/<int:pk>/', DeleteOfferView.as_view(), name='delete_offer'),
    path('pause_offer/<int:pk>/', PauseOfferView.as_view(), name='pause_offer'),
    path('unpause_offer/<int:pk>/', UnpauseOfferView.as_view(), name='unpause_offer'),
    path('webmaster/statistics/offers/', WebmasterOfferStatisticsView.as_view(), name='webmaster_offer_statistics'),
    path('webmaster/statistics/financial/', WebmasterFinancialStatisticsView.as_view(),
         name='webmaster_financial_statistics'),
    path('webmaster/clicks/', WebmasterClicksView.as_view(), name='webmaster_clicks'),
]

urlpatterns += [
    path('available_offers/', AvailableOffersView.as_view(), name='available_offers'),
    path('my_offers/', MyOffersView.as_view(), name='my_offers'),
    path('take_offer/<int:offer_id>/', take_offer, name='take_offer'),
    path('remove_offer/<int:offer_id>/', remove_offer, name='remove_offer'),

    path('webmaster/<int:pk>/', WebmasterOfferDetailView.as_view(), name='webmaster_offer_detail'),
    path('webmaster/leads/', WebmasterLeadsView.as_view(), name='webmaster_leads'),
    path('webmaster/leads/trash', WebmasterTrashLeadsView.as_view(), name='webmaster_trash_leads'),


    path('advertiser/statistics/offers/', AdvertiserOfferStatisticsView.as_view(), name='advertiser_offer_statistics'),
    path('advertiser/statistics/financial/', AdvertiserFinancialStatisticsView.as_view(),
         name='advertiser_financial_statistics'),

    path('admin/statistics/offers/', AdminOfferStatisticsView.as_view(), name='admin_offer_statistics'),

    path('advertiser/leads/', AdvertiserLeadsView.as_view(), name='advertiser_leads'),
    path('add-comment/', add_comment, name='add_comment'),

    path('download-archive/<int:pk>/', download_offer_archive, name='download_offer_archive'),
    path('add-metrika-token/<int:pk>/', AddMetrikaTokenView.as_view(), name='add_metrika_token'),

]
