import os

import requests
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Sum, Q
from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import ListView, CreateView, DetailView, DeleteView, View
from django.contrib import messages
from .models import Offer, LeadWall, OfferWebmaster, Click, LeadComment, OfferArchive
from .forms import OfferForm, OfferWebmasterForm
from user_accounts.models import Advertiser, Webmaster
from datetime import date, datetime
from django.db import models, transaction
from django.core.paginator import Paginator


def get_geolocation(ip):
    try:
        response = requests.get(f'http://ipinfo.io/{ip}/json')
        data = response.json()
        return f"{data.get('city', '')}, {data.get('region', '')}, {data.get('country', '')}"
    except Exception as e:
        return "Unknown Location"

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем кастомные данные в контекст
        try:
            webmaster = get_object_or_404(Webmaster, user=self.request.user)
            context['my_offers_count'] = Offer.objects.filter(webmaster_links__webmaster=webmaster).count()
        except Http404:
            context['my_offers_count'] = ''

        return context

class MyOffersView(LoginRequiredMixin, ListView):
    model = Offer
    template_name = 'offers/my_offers.html'
    context_object_name = 'offers'
    paginate_by = 25

    def get_queryset(self):
        webmaster = get_object_or_404(Webmaster, user=self.request.user)
        return Offer.objects.filter(webmaster_links__webmaster=webmaster)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем кастомные данные в контекст
        context['all_offers_count'] = Offer.objects.filter(public_status='public', status='registered').count()
        # return Offer.objects.filter(public_status='public', status='registered').count()
        return context


@login_required
def take_offer(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)
    webmaster = get_object_or_404(Webmaster, user=request.user)
    # Проверка, что связь еще не создана
    if not OfferWebmaster.objects.filter(offer=offer, webmaster=webmaster).exists():
        OfferWebmaster.objects.create(offer=offer, webmaster=webmaster)

    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def remove_offer(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)
    webmaster = get_object_or_404(Webmaster, user=request.user)
    # Проверка, что связь еще не создана
    if OfferWebmaster.objects.filter(offer=offer, webmaster=webmaster).exists():
        OfferWebmaster.objects.filter(offer=offer, webmaster=webmaster).delete()

    return redirect(request.META.get('HTTP_REFERER', '/'))


class WebmasterOfferDetailView(LoginRequiredMixin, DetailView):
    model = Offer
    template_name = 'offers/webmaster_offer_detail.html'
    context_object_name = 'offer'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        webmaster = get_object_or_404(Webmaster, user=self.request.user)
        offer_webmaster = get_object_or_404(OfferWebmaster, offer=self.object, webmaster=webmaster)

        # Инициализируем форму для метрики только для вебмастера
        metrika_form = OfferWebmasterForm(instance=offer_webmaster, initial={'is_webmaster': True})

        context['offer_webmaster'] = offer_webmaster
        context['metrika_form'] = metrika_form
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        webmaster = get_object_or_404(Webmaster, user=self.request.user)
        offer_webmaster = get_object_or_404(OfferWebmaster, offer=self.object, webmaster=webmaster)

        # Проверяем, если это вебмастер, обрабатываем форму
        metrika_form = OfferWebmasterForm(request.POST, instance=offer_webmaster, initial={'is_webmaster': True})
        if metrika_form.is_valid():
            metrika_form.save()
            messages.success(request, 'Ключ Яндекс Метрики успешно обновлен.')
        else:
            messages.error(request, 'Ошибка при обновлении ключа Яндекс Метрики.')

        return redirect('webmaster_offer_detail', pk=self.object.pk)


class WebmasterLeadsView(LoginRequiredMixin, ListView):
    model = LeadWall
    template_name = 'leads/webmaster_leads.html'
    context_object_name = 'leads'
    paginate_by = 25  # Устанавливаем количество элементов на страницу

    def get_queryset(self):
        webmaster = get_object_or_404(Webmaster, user=self.request.user)
        queryset = LeadWall.objects.filter(offer_webmaster__webmaster=webmaster).order_by('-id')

        el_id = self.request.GET.get('id')

        offer_id = self.request.GET.get('offer_id')
        status = self.request.GET.get('lead_status')
        domain_name = self.request.GET.get('domain_name')
        name = self.request.GET.get('name')
        processing_status = self.request.GET.get('precessing_status')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        sub_filters = {f"sub_{i}": self.request.GET.get(f"sub_{i}") for i in range(1, 6)}

        if el_id:
            queryset = queryset.filter(id=el_id)

        if offer_id:
            queryset = queryset.filter(offer_webmaster__offer__id=offer_id)

        if domain_name:
            queryset = queryset.filter(domain=domain_name)

        if name:
            queryset = queryset.filter(name=name)


        if status:
            queryset = queryset.filter(status=status)

        if processing_status:
            queryset = queryset.filter(processing_status=processing_status)

        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)

        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)

        for key, value in sub_filters.items():
            if value:
                queryset = queryset.filter(**{key: value})

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        webmaster = get_object_or_404(Webmaster, user=self.request.user)
        context['offers'] = Offer.objects.filter(webmaster_links__webmaster=webmaster)
        return context

@require_POST
@login_required
def add_comment(request):
    lead_id = request.POST.get('lead_id')
    text = request.POST.get('text')

    if not lead_id or not text:
        return JsonResponse({'success': False, 'message': 'Необходимо указать ID лида и текст комментария.'}, status=400)

    # Получаем лид по его ID
    lead = get_object_or_404(LeadWall, id=lead_id)

    # Создаем новый комментарий
    comment = LeadComment.objects.create(user=request.user, lead=lead, text=text)

    # Форматируем данные для отправки в ответе
    comment_data = {
        'user': comment.user.username,
        'text': comment.text,
        'created_at': comment.created_at.strftime('%d.%m.%Y %H:%M:%S')
    }

    return JsonResponse({'success': True, 'comment': comment_data})


class AdvertiserLeadsView(LoginRequiredMixin, ListView):
    model = LeadWall
    template_name = 'leads/advertiser_leads.html'
    context_object_name = 'leads'
    paginate_by = 25

    def get_queryset(self):
        advertiser = get_object_or_404(Advertiser, user=self.request.user)
        queryset = LeadWall.objects.filter(offer_webmaster__offer__partner_card__advertiser=advertiser).order_by('-id')

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
            text = request.POST.get('text')
            new_processing_status = request.POST.get('processing_status')

            if text:  # Если это добавление комментария
                lead = get_object_or_404(LeadWall, id=lead_id)
                comment = LeadComment.objects.create(user=request.user, lead=lead, text=text)
                return JsonResponse({'success': True, 'comment': {'user': comment.user.username, 'text': comment.text,
                                                                  'created_at': comment.created_at}})

            if new_processing_status:  # Если это изменение статуса обработки
                lead = get_object_or_404(LeadWall, id=lead_id)

                if lead.processing_status in ['new', 'no_response'] and lead.can_change_to(new_processing_status):
                    lead.processing_status = new_processing_status

                    if new_processing_status in ['callback', 'appointment', 'visit']:
                        lead.status = 'paid'
                        lead.offer_webmaster.offer.partner_card.deposit -= lead.offer_webmaster.offer.lead_price
                        lead.offer_webmaster.webmaster.balance += lead.offer_webmaster.offer.lead_price
                        lead.offer_webmaster.webmaster.save()
                        lead.offer_webmaster.offer.partner_card.save()

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
        # Получение текущего вебмастера
        webmaster = get_object_or_404(Webmaster, user=self.request.user)

        offers = OfferWebmaster.objects.filter(webmaster=webmaster)

        # Инициализация переменной offer_stats
        offer_stats = []

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

        # Подсчёт кликов для расчёта EPC
        clicks = Click.objects.filter(offer_webmaster__in=offers)
        if start_date:
            clicks = clicks.filter(created_at__gte=datetime.strptime(start_date, '%Y-%m-%d'))
        if end_date:
            clicks = clicks.filter(created_at__lte=datetime.strptime(end_date, '%Y-%m-%d'))
        if offer_id:
            clicks = clicks.filter(offer_webmaster__offer_id=offer_id)

        click_counts = clicks.values('offer_webmaster__offer__id').annotate(total_clicks=Count('id')).order_by()

        clicks_dict = {item['offer_webmaster__offer__id']: item['total_clicks'] for item in click_counts}

        if all_time:
            # Группировка по офферам за всё время
            offer_stats = leads.values('offer_webmaster__offer__name', 'offer_webmaster__offer__id').annotate(
                unique_leads=Count('id', distinct=True),
                approved_leads=Count('id', filter=Q(status='paid')),
                new_leads=Count('id', filter=Q(status='on_hold')),
                rejected_leads=Count('id', filter=Q(status='cancelled')),
                trash_leads=Count('id', filter=Q(processing_status='trash')),
                duplicate_leads=Count('id', filter=Q(processing_status='duplicate'))
            ).order_by('offer_webmaster__offer__name')

            for stat in offer_stats:
                offer_id = stat['offer_webmaster__offer__id']
                total_clicks = clicks_dict.get(offer_id, 0)
                lead_price = Offer.objects.get(id=offer_id).lead_price  # Получение стоимости лида из оффера
                stat['total_income'] = stat['approved_leads'] * lead_price  # Расчет дохода
                stat['approve_percent'] = (stat['approved_leads'] / stat['unique_leads'] * 100) if stat['unique_leads'] > 0 else 0
                stat['conversion_rate'] = (stat['unique_leads'] / total_clicks * 100) if total_clicks > 0 else 0
                stat['epc'] = (stat['total_income'] / total_clicks) if total_clicks > 0 else 0

        else:
            # Группировка по дате
            offer_stats = leads.values('created_at__date').annotate(
                unique_leads=Count('id', distinct=True),
                approved_leads=Count('id', filter=Q(status='paid')),
                new_leads=Count('id', filter=Q(status='on_hold')),
                rejected_leads=Count('id', filter=Q(status='cancelled')),
                trash_leads=Count('id', filter=Q(processing_status='trash')),
                duplicate_leads=Count('id', filter=Q(processing_status='duplicate'))
            ).order_by('created_at__date')

            for stat in offer_stats:
                # Здесь не используется ключ 'offer_webmaster__offer__id', поскольку группировка идет по дате
                total_clicks = clicks.filter(created_at__date=stat['created_at__date']).count()
                lead_price = offers.aggregate(Sum('offer__lead_price'))['offer__lead_price__sum'] or 0
                stat['total_income'] = stat['approved_leads'] * lead_price  # Расчет дохода
                stat['approve_percent'] = (stat['approved_leads'] / stat['unique_leads'] * 100) if stat['unique_leads'] > 0 else 0
                stat['conversion_rate'] = (stat['unique_leads'] / total_clicks * 100) if total_clicks > 0 else 0
                stat['epc'] = (stat['total_income'] / total_clicks) if total_clicks > 0 else 0

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




class WebmasterClicksView(LoginRequiredMixin, ListView):
    model = Click
    template_name = 'clicks/webmaster_clicks.html'
    context_object_name = 'clicks'
    paginate_by = 25  # Устанавливаем количество элементов на страницу

    def get_queryset(self):
        webmaster = get_object_or_404(Webmaster, user=self.request.user)
        queryset = Click.objects.filter(offer_webmaster__webmaster=webmaster)

        offer_id = self.request.GET.get('offer_id')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        sub_1 = self.request.GET.get('sub_1')
        sub_2 = self.request.GET.get('sub_2')
        sub_3 = self.request.GET.get('sub_3')
        sub_4 = self.request.GET.get('sub_4')
        sub_5 = self.request.GET.get('sub_5')

        if offer_id:
            queryset = queryset.filter(offer_webmaster__offer__id=offer_id)

        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)

        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)

        if sub_1:
            queryset = queryset.filter(sub_1=sub_1)

        if sub_2:
            queryset = queryset.filter(sub_2=sub_2)

        if sub_3:
            queryset = queryset.filter(sub_3=sub_3)

        if sub_4:
            queryset = queryset.filter(sub_4=sub_4)

        if sub_5:
            queryset = queryset.filter(sub_5=sub_5)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        webmaster = get_object_or_404(Webmaster, user=self.request.user)
        context['offers'] = Offer.objects.filter(webmaster_links__webmaster=webmaster)
        return context

def download_offer_archive(request, pk):
    try:
        # Получаем объект архива
        offer_archive = OfferArchive.objects.get(offer_id=pk)
        file_path = offer_archive.local_repo_path + '.zip'  # Путь к архиву ZIP

        if os.path.exists(file_path):
            # Открываем файл архива и возвращаем его как ответ
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type='application/zip')
                response['Content-Disposition'] = f'attachment; filename={os.path.basename(file_path)}'
                return response
        else:
            raise Http404("Архив не найден.")
    except OfferArchive.DoesNotExist:
        raise Http404("Архив для данного оффера не найден.")