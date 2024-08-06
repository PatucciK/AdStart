from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, DetailView, DeleteView, View
from django.contrib import messages
from .models import Offer, LeadWall
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


class WebmasterLeadsView(LoginRequiredMixin, ListView):
    model = LeadWall
    template_name = 'leads/webmaster_leads.html'
    context_object_name = 'leads'

    def get_queryset(self):
        webmaster = get_object_or_404(Webmaster, user=self.request.user)
        queryset = LeadWall.objects.filter(offer__webmaster=webmaster)

        # Получаем параметры фильтрации
        offer_id = self.request.GET.get('offer_id')
        status = self.request.GET.get('status')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        # Фильтрация по офферу
        if offer_id:
            queryset = queryset.filter(offer__id=offer_id)

        # Фильтрация по статусу
        if status:
            queryset = queryset.filter(status=status)

        # Фильтрация по дате
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)

        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        webmaster = get_object_or_404(Webmaster, user=self.request.user)
        context['offers'] = webmaster.offers.all()
        return context

class AdvertiserLeadsView(LoginRequiredMixin, ListView):
    model = LeadWall
    template_name = 'leads/advertiser_leads.html'
    context_object_name = 'leads'

    def get_queryset(self):
        advertiser = get_object_or_404(Advertiser, user=self.request.user)
        queryset = LeadWall.objects.filter(offer__partner_card__advertiser=advertiser)

        offer_id = self.request.GET.get('offer_id')
        status = self.request.GET.get('status')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        if offer_id:
            queryset = queryset.filter(offer__id=offer_id)

        if status:
            queryset = queryset.filter(status=status)

        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)

        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)

        return queryset

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            lead_id = request.POST.get('lead_id')
            new_status = request.POST.get('status')
            lead = get_object_or_404(LeadWall, id=lead_id)

            if lead.can_change_to(new_status):
                lead.status = new_status
                lead.save()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'message': 'Нельзя изменить на этот статус.'})

        return JsonResponse({'success': False, 'message': 'Неверный запрос или метод запроса не является AJAX.'}, status=400)