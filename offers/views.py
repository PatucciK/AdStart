from django.views.generic import ListView
from .models import Offer
from django.contrib.auth.mixins import LoginRequiredMixin
from user_accounts.models import Advertiser

class AdvertiserOffersView(LoginRequiredMixin, ListView):
    model = Offer
    template_name = 'offers/advertiser_offers.html'
    context_object_name = 'offers'

    def get_queryset(self):
        advertiser = Advertiser.objects.get(user=self.request.user)
        return Offer.objects.filter(partner_card__advertiser=advertiser)
