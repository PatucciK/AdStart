from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Sum, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, DetailView, DeleteView, View
from django.contrib import messages
from .models import Offer, LeadWall, OfferWebmaster
from .forms import OfferForm
from user_accounts.models import Advertiser, Webmaster
from datetime import date, datetime
from django.db import models, transaction
from django.core.paginator import Paginator


class AdvertiserOffersView(LoginRequiredMixin, ListView):
    model = Offer
    template_name = 'offers/advertiser_offers.html'
    context_object_name = 'offers'
    paginate_by = 25

    def get_queryset(self):
        advertiser = Advertiser.objects.get(user=self.request.user)
        # Добавьте сортировку здесь, например, по полю id или любому другому
        return Offer.objects.filter(partner_card__advertiser=advertiser).order_by('-id')



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
    paginate_by = 25

    def get_queryset(self):
        # Добавьте сортировку здесь
        return Offer.objects.filter(public_status='public', status='registered').order_by('-id')


class MyOffersView(LoginRequiredMixin, ListView):
    model = Offer
    template_name = 'offers/my_offers.html'
    context_object_name = 'offers'
    paginate_by = 25

    def get_queryset(self):
        webmaster = get_object_or_404(Webmaster, user=self.request.user)
        return Offer.objects.filter(webmaster_links__webmaster=webmaster)


@login_required
def take_offer(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)
    webmaster = get_object_or_404(Webmaster, user=request.user)
    # Проверка, что связь еще не создана
    if not OfferWebmaster.objects.filter(offer=offer, webmaster=webmaster).exists():
        OfferWebmaster.objects.create(offer=offer, webmaster=webmaster)
        return redirect('my_offers')
    return redirect('available_offers')


class WebmasterOfferDetailView(LoginRequiredMixin, DetailView):
    model = Offer
    template_name = 'offers/webmaster_offer_detail.html'
    context_object_name = 'offer'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        webmaster = get_object_or_404(Webmaster, user=self.request.user)
        offer_webmaster = get_object_or_404(OfferWebmaster, offer=self.object, webmaster=webmaster)
        context['offer_webmaster'] = offer_webmaster
        return context

class WebmasterLeadsView(LoginRequiredMixin, ListView):
    model = LeadWall
    template_name = 'leads/webmaster_leads.html'
    context_object_name = 'leads'
    paginate_by = 25  # Устанавливаем количество элементов на страницу

    def get_queryset(self):
        webmaster = get_object_or_404(Webmaster, user=self.request.user)
        queryset = LeadWall.objects.filter(offer_webmaster__webmaster=webmaster)

        offer_id = self.request.GET.get('offer_id')
        status = self.request.GET.get('status')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        if offer_id:
            queryset = queryset.filter(offer_webmaster__offer__id=offer_id)

        if status:
            queryset = queryset.filter(status=status)

        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)

        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)

        return queryset


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        webmaster = get_object_or_404(Webmaster, user=self.request.user)
        context['offers'] = Offer.objects.filter(webmaster_links__webmaster=webmaster)
        return context


class AdvertiserLeadsView(LoginRequiredMixin, ListView):
    model = LeadWall
    template_name = 'leads/advertiser_leads.html'
    context_object_name = 'leads'
    paginate_by = 25

    def get_queryset(self):
        advertiser = get_object_or_404(Advertiser, user=self.request.user)
        queryset = LeadWall.objects.filter(offer_webmaster__offer__partner_card__advertiser=advertiser)

        offer_id = self.request.GET.get('offer_id')
        status = self.request.GET.get('status')
        processing_status = self.request.GET.get('processing_status')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        if offer_id:
            queryset = queryset.filter(offer_webmaster__offer__id=offer_id)

        if status:
            queryset = queryset.filter(status=status)

        if processing_status:
            queryset = queryset.filter(processing_status=processing_status)

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
            new_processing_status = request.POST.get('processing_status')
            lead = get_object_or_404(LeadWall, id=lead_id)

            # Разрешить изменение только если текущий статус обработки - 'new' или 'no_response'
            if lead.processing_status in ['new', 'no_response'] and lead.can_change_to(new_processing_status):
                lead.processing_status = new_processing_status

                # Если новый статус - 'callback', 'appointment' или 'visit', установить статус как 'paid'
                if new_processing_status in ['callback', 'appointment', 'visit']:
                    lead.status = 'paid'
                    lead.offer_webmaster.offer.partner_card.deposit -= lead.offer_webmaster.offer.lead_price
                    lead.offer_webmaster.webmaster.balance += lead.offer_webmaster.offer.lead_price
                    lead.offer_webmaster.webmaster.save()
                    lead.offer_webmaster.offer.partner_card.save()

                # Если новый статус - 'rejected', установить статус как 'cancelled'
                elif new_processing_status == 'rejected':
                    lead.status = 'cancelled'

                lead.save()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'message': 'Нельзя изменить на этот статус.'})

        return JsonResponse({'success': False, 'message': 'Неверный запрос или метод запроса не является AJAX.'},
                            status=400)




class WebmasterOfferStatisticsView(LoginRequiredMixin, ListView):
    model = LeadWall
    template_name = 'statistics/webmaster_offer_statistics.html'
    context_object_name = 'offer_stats'
    paginate_by = 25

    def get_queryset(self):
        # Получите текущего вебмастера
        webmaster = get_object_or_404(Webmaster, user=self.request.user)

        offers = OfferWebmaster.objects.filter(webmaster=webmaster)

        # Извлечение фильтров из запроса
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        offer_id = self.request.GET.get('offer_id')
        all_time = self.request.GET.get('all_time')

        # Фильтрация по дате и офферам
        lead_filter = Q(offer_webmaster__in=offers)
        if start_date:
            lead_filter &= Q(created_at__gte=datetime.strptime(start_date, '%Y-%m-%d'))
        if end_date:
            lead_filter &= Q(created_at__lte=datetime.strptime(end_date, '%Y-%m-%d'))
        if offer_id:
            lead_filter &= Q(offer_webmaster__offer_id=offer_id)

        leads = LeadWall.objects.filter(lead_filter)

        # Группировка статистики
        if all_time:
            # Группировка по офферу за все время
            offer_stats = leads.values('offer_webmaster__offer__name', 'offer_webmaster__offer__id').annotate(
                unique_leads=Count('id', distinct=True),
                approved_leads=Count('id', filter=Q(status='paid')),
                new_leads=Count('id', filter=Q(status='on_hold')),
                rejected_leads=Count('id', filter=Q(status='cancelled'))
            ).order_by('offer_webmaster__offer__name')

            for stat in offer_stats:
                stat['group_date'] = 'За все время'  # Используем общий заголовок для группировки
                stat['approve_percent'] = (stat['approved_leads'] / stat['unique_leads'] * 100) if stat[
                                                                                                       'unique_leads'] > 0 else 0

        else:
            # Группировка по дате
            offer_stats = leads.values('offer_webmaster__offer__name', 'offer_webmaster__offer__id',
                                       'created_at__date').annotate(
                unique_leads=Count('id', distinct=True),
                approved_leads=Count('id', filter=Q(status='paid')),
                new_leads=Count('id', filter=Q(status='on_hold')),
                rejected_leads=Count('id', filter=Q(status='cancelled'))
            ).order_by('created_at__date')

            for stat in offer_stats:
                stat['group_date'] = stat['created_at__date']
                stat['approve_percent'] = (stat['approved_leads'] / stat['unique_leads'] * 100) if stat[
                                                                                                       'unique_leads'] > 0 else 0

        return offer_stats

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['offers'] = OfferWebmaster.objects.filter(webmaster=self.request.user.webmaster)
        return context



class WebmasterFinancialStatisticsView(LoginRequiredMixin, View):
    template_name = 'statistics/webmaster_financial_statistics.html'
    paginate_by = 50

    def get(self, request, *args, **kwargs):
        webmaster = get_object_or_404(Webmaster, user=request.user)
        offers = Offer.objects.filter(webmaster_links__webmaster=webmaster)

        # Get filters from request
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        offer_id = request.GET.get('offer_id')

        # Base filter
        lead_filter = Q(offer_webmaster__webmaster=webmaster)
        if start_date:
            lead_filter &= Q(created_at__gte=datetime.strptime(start_date, '%Y-%m-%d'))
        if end_date:
            lead_filter &= Q(created_at__lte=datetime.strptime(end_date, '%Y-%m-%d'))
        if offer_id:
            lead_filter &= Q(offer_webmaster__offer__id=offer_id)

        # Fetch leads
        leads = LeadWall.objects.filter(lead_filter)

        # Financial stats
        financial_stats = leads.values('offer_webmaster__offer__name', 'offer_webmaster__offer__id').annotate(
            accepted_leads=Count('id', filter=Q(status__in=['visit', 'appointment', 'paid', 'expired'])),
            earned=Sum('offer_webmaster__offer__lead_price', filter=Q(status__in=['visit', 'appointment', 'paid', 'expired'])),
        ).order_by('offer_webmaster__offer__name')

        # Calculate date range
        if start_date or end_date:
            for stat in financial_stats:
                related_leads = leads.filter(
                    offer_webmaster__offer__id=stat['offer_webmaster__offer__id']
                )
                first_lead_date = related_leads.earliest('created_at').created_at.date()
                last_lead_date = related_leads.latest('created_at').created_at.date()
                stat['date_range'] = f"{first_lead_date} - {last_lead_date}"
        else:
            for stat in financial_stats:
                stat['date_range'] = "За все время"

        context = {
            'offers': offers,
            'financial_stats': financial_stats
        }
        return render(request, self.template_name, context)


class AdvertiserOfferStatisticsView(LoginRequiredMixin, View):
    template_name = 'statistics/advertiser_offer_statistics.html'
    paginate_by = 50

    def get(self, request, *args, **kwargs):
        advertiser = get_object_or_404(Advertiser, user=request.user)
        offers = Offer.objects.filter(partner_card__advertiser=advertiser)

        # Получение фильтров из запроса
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        offer_id = request.GET.get('offer_id')

        # Фильтрация по дате и офферам
        lead_filter = Q(offer_webmaster__offer__partner_card__advertiser=advertiser)
        if start_date:
            lead_filter &= Q(created_at__gte=datetime.strptime(start_date, '%Y-%m-%d'))
        if end_date:
            lead_filter &= Q(created_at__lte=datetime.strptime(end_date, '%Y-%m-%d'))
        if offer_id:
            lead_filter &= Q(offer_webmaster__offer__id=offer_id)

        leads = LeadWall.objects.filter(lead_filter)

        # Статистика по офферам
        offer_stats = leads.values('offer_webmaster__offer__name', 'offer_webmaster__offer__id', 'created_at').annotate(
            unique_leads=Count('id', distinct=True),
            approved_leads=Count('id', filter=Q(status__in=['visit', 'appointment', 'paid', 'expired'])),
            new_leads=Count('id', filter=Q(processing_status='new')),
            rejected_leads=Count('id', filter=Q(
                processing_status__in=['no_response', 'callback', 'appointment', 'visit', 'trash', 'duplicate']))
        ).order_by('created_at')

        for stat in offer_stats:
            stat['approve_percent'] = (stat['approved_leads'] / stat['unique_leads'] * 100) if stat[
                                                                                                   'unique_leads'] > 0 else 0

        context = {
            'offers': offers,
            'offer_stats': offer_stats
        }
        return render(request, self.template_name, context)


class AdvertiserFinancialStatisticsView(LoginRequiredMixin, View):
    template_name = 'statistics/advertiser_financial_statistics.html'
    paginate_by = 50

    def get(self, request, *args, **kwargs):
        advertiser = get_object_or_404(Advertiser, user=request.user)
        offers = Offer.objects.filter(partner_card__advertiser=advertiser)

        # Получение фильтров из запроса
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        offer_id = request.GET.get('offer_id')

        # Фильтрация по дате и офферам
        lead_filter = Q(offer_webmaster__offer__in=offers)
        if start_date:
            lead_filter &= Q(created_at__gte=datetime.strptime(start_date, '%Y-%m-%d'))
        if end_date:
            lead_filter &= Q(created_at__lte=datetime.strptime(end_date, '%Y-%m-%d'))
        if offer_id:
            try:
                # Найдите UUID для предоставленного offer_id
                offer_uuid = Offer.objects.get(id=offer_id).unique_token
                lead_filter &= Q(offer_webmaster__offer_id=offer_uuid)
            except Offer.DoesNotExist:
                # Если оффер не найден, установите lead_filter так, чтобы он не возвращал результатов
                lead_filter &= Q(pk__in=[])

        leads = LeadWall.objects.filter(lead_filter)

        # Финансовая статистика
        financial_stats = leads.values('offer_webmaster__offer__name', 'offer_webmaster__offer__id', 'offer_webmaster__webmaster__user__username').annotate(
            accepted_leads=Count('id', filter=Q(status__in=['visit', 'appointment', 'paid', 'expired'])),
            spent=Sum('offer_webmaster__offer__lead_price', filter=Q(status__in=['visit', 'appointment', 'paid', 'expired'])),
        ).order_by('offer_webmaster__offer__name')

        context = {
            'offers': offers,
            'financial_stats': financial_stats
        }
        return render(request, self.template_name, context)
