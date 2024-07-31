from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, DeleteView, View
from django.contrib import messages
from .models import Offer
from .forms import OfferForm
from user_accounts.models import Advertiser, Webmaster
from datetime import date


class AdvertiserOffersView(LoginRequiredMixin, ListView):
    model = Offer
    template_name = 'offers/advertiser_offers.html'
    context_object_name = 'offers'

    def get_queryset(self):
        advertiser = Advertiser.objects.get(user=self.request.user)
        return Offer.objects.filter(partner_card__advertiser=advertiser)


class CreateOfferView(LoginRequiredMixin, CreateView):
    model = Offer
    form_class = OfferForm
    template_name = 'offers/create_offer.html'

    def form_valid(self, form):
        form.instance.partner_card = self.request.user.advertiser.partner_card
        form.instance.contract_number = self.generate_contract_number()
        form.instance.contract_date = date.today()
        form.instance.status = 'registered'
        return super().form_valid(form)

    def generate_contract_number(self):
        # Логика для генерации номера договора
        return "CN-" + str(Offer.objects.count() + 1)

    def get_success_url(self):
        return reverse('advertiser_offers')


class OfferDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Offer
    template_name = 'offers/offer_detail.html'

    def test_func(self):
        offer = self.get_object()
        return self.request.user.is_superuser or offer.partner_card.advertiser.user == self.request.user


class PauseOfferView(LoginRequiredMixin, UserPassesTestMixin, View):
    def post(self, request, *args, **kwargs):
        offer = get_object_or_404(Offer, pk=kwargs['pk'])
        if offer.status == 'registered':
            offer.status = 'paused'
            offer.save()
            messages.success(request, 'Оффер поставлен на паузу.')
        return redirect('offer_detail', pk=offer.pk)

    def test_func(self):
        offer = get_object_or_404(Offer, pk=self.kwargs['pk'])
        return self.request.user.is_superuser or offer.partner_card.advertiser.user == self.request.user


class UnpauseOfferView(LoginRequiredMixin, UserPassesTestMixin, View):
    def post(self, request, *args, **kwargs):
        offer = get_object_or_404(Offer, pk=kwargs['pk'])
        if offer.status == 'paused':
            offer.status = 'registered'
            offer.save()
            messages.success(request, 'Оффер возвращен в статус регистрации.')
        return redirect('offer_detail', pk=offer.pk)

    def test_func(self):
        offer = get_object_or_404(Offer, pk=self.kwargs['pk'])
        return self.request.user.is_superuser or offer.partner_card.advertiser.user == self.request.user


class DeleteOfferView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Offer
    template_name = 'offers/offer_confirm_delete.html'
    success_url = reverse_lazy('advertiser_offers')

    def test_func(self):
        offer = self.get_object()
        return self.request.user.is_superuser or offer.partner_card.advertiser.user == self.request.user


class AvailableOffersView(LoginRequiredMixin, ListView):
    model = Offer
    template_name = 'offers/available_offers.html'
    context_object_name = 'offers'

    def get_queryset(self):
        return Offer.objects.filter(public_status='public', status='registered', webmaster=None)


class MyOffersView(LoginRequiredMixin, ListView):
    model = Offer
    template_name = 'offers/my_offers.html'
    context_object_name = 'offers'

    def get_queryset(self):
        webmaster = get_object_or_404(Webmaster, user=self.request.user)
        return Offer.objects.filter(webmaster=webmaster)


@login_required
def take_offer(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)
    webmaster = get_object_or_404(Webmaster, user=request.user)
    if offer.public_status == 'public' and offer.status == 'registered' and offer.webmaster is None:
        offer.webmaster = webmaster
        offer.save()
        return redirect('my_offers')
    return redirect('available_offers')


class WebmasterOfferDetailView(LoginRequiredMixin, DetailView):
    model = Offer
    template_name = 'offers/webmaster_offer_detail.html'
    context_object_name = 'offer'
