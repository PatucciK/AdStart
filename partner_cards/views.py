# partner_cards/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from offers.forms import OfferWebmasterForm
from offers.models import OfferWebmaster
from .models import PartnerCard
from .forms import PartnerCardForm


@login_required
def edit_partner_card(request):
    try:
        partner_card = PartnerCard.objects.get(advertiser=request.user.advertiser)
    except PartnerCard.DoesNotExist:
        partner_card = None

    if request.method == 'POST':
        form = PartnerCardForm(request.POST, request.FILES, instance=partner_card)
        if form.is_valid():
            partner_card = form.save(commit=False)
            partner_card.advertiser = request.user.advertiser
            partner_card.save()
            return redirect('view_partner_card')
    else:
        form = PartnerCardForm(instance=partner_card)

    return render(request, 'partner_cards/edit_partner_card.html', {'form': form})


@login_required
def view_partner_card(request):
    partner_card = PartnerCard.objects.get(advertiser=request.user.advertiser)
    return render(request, 'partner_cards/view_partner_card.html', {'partner_card': partner_card})


class AddMetrikaTokenView(LoginRequiredMixin, UpdateView):
    model = OfferWebmaster
    form_class = OfferWebmasterForm
    template_name = 'offers/add_metrika_token.html'

    def get_object(self, queryset=None):
        return get_object_or_404(OfferWebmaster, pk=self.kwargs['pk'], webmaster__user=self.request.user)

    def form_valid(self, form):
        form.save()
        return redirect(reverse_lazy('webmaster_offer_detail', kwargs={'pk': self.get_object().offer.pk}))