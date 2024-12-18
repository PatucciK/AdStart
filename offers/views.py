import os
from calendar import month
from collections import defaultdict
from lib2to3.fixes.fix_input import context

import requests
from datetime import datetime, timedelta
from collections import Counter
from celery.bin.control import status
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Sum, Q, Value
from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import ListView, CreateView, DetailView, DeleteView, View
from django.contrib import messages
from django.db.models.functions import TruncMonth, Coalesce
from .models import Offer, LeadWall, OfferWebmaster, Click, LeadComment, OfferArchive
from sites.models import Category, SiteArchive
from partner_cards.models import PartnerCard
from .forms import OfferForm, OfferWebmasterForm
from user_accounts.models import Advertiser, Webmaster
from datetime import date, datetime
from django.db import models, transaction
from django.db.models import F

from django.core.paginator import Paginator


import locale

try:
    locale.setlocale(locale.LC_ALL, "ru_RU.utf8")
except locale.Error:
    # Используем локаль по умолчанию
    locale.setlocale(locale.LC_ALL, 'en_US.utf8')

def get_geolocation(ip):
    try:
        response = requests.get(f'http://ipinfo.io/{ip}/json')
        data = response.json()
        return f"{data.get('city', '')}, {data.get('region', '')}, {data.get('country', '')}"
    except Exception as e:
        return "Unknown Location"

def schedule_update(request, pk):
    # Запуск задачи с отложенным выполнением через 24 часа
    update_record.apply_async((pk,), countdown=86400)  # 86400 секунд = 24 часа
    return HttpResponse(f'Задача на обновление записи {pk} запланирована.')


class AdvertiserOffersView(LoginRequiredMixin, ListView):
    model = Offer
    template_name = 'offers/advertiser_offers.html'
    context_object_name = 'offers'
    paginate_by = 25

    def get_queryset(self):
        advertiser = Advertiser.objects.get(user=self.request.user)
        # Добавьте сортировку здесь, например, по полю id или любому другому
        if self.request.user.is_superuser:
            offers = Offer.objects.all().order_by('-id')

        else:
            offers = Offer.objects.filter(partner_card__advertiser=advertiser).order_by('-id')

        return offers



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


class OfferDetailView(LoginRequiredMixin, DetailView):
    model = Offer
    context_object_name = 'offer'

    def get_template_names(self):
        try:
            webmaster = Webmaster.objects.get(user=self.request.user)
            offer_webmaster = OfferWebmaster.objects.get(offer_id=self.kwargs['pk'], webmaster=webmaster)
        except Webmaster.DoesNotExist:
            return ['offers/offer_detail.html']
        except OfferWebmaster.DoesNotExist:
            return ['offers/offer_detail.html']
        
        return ['offers/webmaster_offer_detail.html']


    def get_queryset(self):
        print(self.kwargs['pk'])
        offer = Offer.objects.filter(id=self.kwargs['pk'])
        return offer

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            webmaster = Webmaster.objects.get(user=self.request.user)
            offer_webmaster = OfferWebmaster.objects.filter(offer_id=self.kwargs['pk'], webmaster=webmaster).first()
            if offer_webmaster:
                metrika_form = OfferWebmasterForm(instance=offer_webmaster, initial={'is_webmaster': True})
                context['metrika_form'] = metrika_form 
                context['offer_webmaster'] = offer_webmaster
        except Webmaster.DoesNotExist:
            offer_webmaster = OfferWebmaster.objects.filter(offer_id=self.kwargs['pk'])
            web_ids = [i['webmaster_id'] for i in offer_webmaster.values('webmaster_id')]
            web = Webmaster.objects.all()

            free_web = []

            for obj in web:
                if obj.id not in web_ids:
                    free_web.append(obj)

            context['webmasters'] = free_web

        context['offer_web'] = offer_webmaster
        category_site = Category.objects.all()
        context['category_site'] = category_site        

        context['sites'] = SiteArchive.objects.filter(offer_id=self.kwargs['pk'])       
        print()

        return context

    def post(self, request, *args, **kwargs):

        action = request.POST.get('action')

        offer = get_object_or_404(Offer, pk=kwargs['pk'])


        if action == 'add_offerweb':
            webmaster_id = request.POST.get('webmaster')
            payout_input = request.POST.get('payoutInput')
            webmaster = Webmaster.objects.get(id=webmaster_id)

            if int(payout_input) < offer.offer_price:
                if not OfferWebmaster.objects.filter(offer=offer, webmaster=webmaster).exists():
                    OfferWebmaster.objects.create(offer=offer, webmaster=webmaster,
                                                  validation_data_lead=offer.validation_data_web, rate_of_pay=payout_input)

        elif action == 'remove_offerweb':
            webmaster_id = request.POST.get('webmaster')
            payout_input = request.POST.get('payoutInput')
            webmaster = Webmaster.objects.get(id=webmaster_id)
            if OfferWebmaster.objects.filter(offer=offer, webmaster=webmaster).exists():
                OfferWebmaster.objects.filter(offer=offer, webmaster=webmaster).delete()
            
        elif action == 'add_site':
            site_name = request.POST.get('site_name')
            site_slug = request.POST.get('site_slug')
            site_category = Category.objects.get(slug=request.POST.get('category'))
            site_archive = request.FILES.get('uploaded_file')
            if not SiteArchive.objects.filter(slug=site_slug, name=site_name).exists():
                SiteArchive.objects.create(offer=offer, name=site_name, slug=site_slug, category=site_category, archive=site_archive)
        
        elif action == 'delete_site':

            site = request.POST.get('site')
            if SiteArchive.objects.filter(id=site).exists():
                SiteArchive.objects.filter(id=site).delete()

        return redirect('offer_detail', pk=offer.pk)

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

    def post(self, request, *args, **kwargs):
        pass

    def test_func(self):
        offer = self.get_object()
        return self.request.user.is_superuser or offer.partner_card.advertiser.user == self.request.user


class AvailableOffersView(LoginRequiredMixin, ListView):
    model = Offer
    template_name = 'offers/available_offers.html'
    context_object_name = 'offers'
    paginate_by = 25

    def get_queryset(self):
        queryset = Offer.objects.filter(public_status='public', status='registered').order_by('-id')

        el_id = self.request.GET.get('id')
        company_name = self.request.GET.getlist('company_name[]')
        offer_name = self.request.GET.get('offer')
        status_of = self.request.GET.get('status')
        geo = self.request.GET.get('geo')

        if el_id:
            queryset = queryset.filter(id=el_id)

        if company_name:
            queryset = queryset.filter(partner_card__in=company_name)

        if offer_name:
            queryset = queryset.filter(name=offer_name)

        if status_of:
            queryset = queryset.filter(status=status_of)

        if geo:
            query = Q()
            for el in geo.split():
                query |= Q(geo__icontains=el)  # Ищем по каждому слову

            # Применяем фильтр с использованием Q-объекта
            queryset = queryset.filter(query)


        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем кастомные данные в контекст
        try:
            webmaster = get_object_or_404(Webmaster, user=self.request.user)
            context['my_offers_count'] = Offer.objects.filter(webmaster_links__webmaster=webmaster).count()
        except Http404:
            context['my_offers_count'] = 0

        try:
            context['companies'] = PartnerCard.objects.values_list('id', 'name')
        except Http404:
            context['companies'] = "Нет информации"

        context['select_companies'] = self.request.GET.getlist('company_name[]')

        return context

class MyOffersView(LoginRequiredMixin, ListView):
    model = Offer
    template_name = 'offers/my_offers.html'
    context_object_name = 'offers'
    paginate_by = 25

    def get_queryset(self):
        webmaster = get_object_or_404(Webmaster, user=self.request.user)


        el_id = self.request.GET.get('id')
        company_name = self.request.GET.getlist('company_name[]')
        offer_name = self.request.GET.get('offer')
        status_of = self.request.GET.get('status')
        geo = self.request.GET.get('geo')

        if el_id:
            webmaster = webmaster.filter(id=el_id)

        if company_name:
            webmaster = webmaster.filter(partner_card__in=company_name)

        if offer_name:
            webmaster = webmaster.filter(name=offer_name)

        if status_of:
            webmaster = webmaster.filter(status=status_of)

        if geo:
            query = Q()
            for el in geo.split():
                query |= Q(geo__icontains=el)  # Ищем по каждому слову

            # Применяем фильтр с использованием Q-объекта
            queryset = webmaster.filter(query)

        return Offer.objects.filter(webmaster_links__webmaster=webmaster)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем кастомные данные в контекст
        context['all_offers_count'] = Offer.objects.filter(public_status='public', status='registered').count()
        # return Offer.objects.filter(public_status='public', status='registered').count()

        try:
            context['companies'] = PartnerCard.objects.values_list('id', 'name')
        except Http404:
            context['companies'] = "Нет информации"

        return context


@login_required
def take_offer(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)
    webmaster = get_object_or_404(Webmaster, user=request.user)
    # Проверка, что связь еще не создана
    if not OfferWebmaster.objects.filter(offer=offer, webmaster=webmaster).exists():
        OfferWebmaster.objects.create(offer=offer, webmaster=webmaster, validation_data_lead=offer.validation_data_web, rate_of_pay=offer.lead_price)

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
        try:
            webmaster = get_object_or_404(Webmaster, user=self.request.user)
            offer_webmaster = get_object_or_404(OfferWebmaster, offer=self.object, webmaster=webmaster)
        except Http404:
            redirect('offer_detail', pk=self.object.pk)
        # Инициализируем форму для метрики только для вебмастера
        metrika_form = OfferWebmasterForm(instance=offer_webmaster, initial={'is_webmaster': True})

        context['offer_webmaster'] = offer_webmaster
        context['metrika_form'] = metrika_form
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            webmaster = get_object_or_404(Webmaster, user=self.request.user)

            offer_webmaster = get_object_or_404(OfferWebmaster, offer=self.object, webmaster=webmaster)
        except Http404:
            redirect('offer_detail', pk=self.object.pk)
        finally:

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
        geo = self.request.GET.get("geo")
        phone_number = self.request.GET.get("phone_number")


        if el_id:
            queryset = queryset.filter(id=el_id)

        if offer_id:
            queryset = queryset.filter(offer_webmaster__offer__id=offer_id)

        if domain_name:
            queryset = queryset.filter(domain__icontains=domain_name)

        if name:
            queryset = queryset.filter(name__icontains=name)

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

        if geo:
            query = Q()
            for el in geo.split():
                query |= Q(geo__icontains=el)  # Ищем по каждому слову

            # Применяем фильтр с использованием Q-объекта
            queryset = queryset.filter(query)

        if phone_number:
            queryset = queryset.filter(phone__icontains=phone_number)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        webmaster = get_object_or_404(Webmaster, user=self.request.user)
        context['offers'] = Offer.objects.filter(webmaster_links__webmaster=webmaster)
        return context

class WebmasterTrashLeadsView(LoginRequiredMixin, ListView):
    model = LeadWall
    template_name = 'leads/webmaster_trash_leads.html'
    context_object_name = 'leads'
    paginate_by = 25  # Устанавливаем количество элементов на страницу

    def get_queryset(self):
        webmaster = get_object_or_404(Webmaster, user=self.request.user)
        queryset = LeadWall.objects.filter(offer_webmaster__webmaster=webmaster, processing_status__in=['trash', 'duplicate']).order_by('-id')

        el_id = self.request.GET.get('id')

        offer_id = self.request.GET.get('offer_id')
        status = self.request.GET.get('lead_status')
        domain_name = self.request.GET.get('domain_name')
        name = self.request.GET.get('name')
        processing_status = self.request.GET.get('precessing_status')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        sub_filters = {f"sub_{i}": self.request.GET.get(f"sub_{i}") for i in range(1, 6)}
        geo = self.request.GET.get("geo")
        phone_number = self.request.GET.get("phone_number")


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

        if geo:
            query = Q()
            for el in geo.split():
                query |= Q(geo__icontains=el)  # Ищем по каждому слову

            # Применяем фильтр с использованием Q-объекта
            queryset = queryset.filter(query)

        if phone_number:
            queryset = queryset.filter(phone=phone_number)

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
        queryset = LeadWall.objects.filter(offer_webmaster__offer__partner_card__advertiser=advertiser).exclude(processing_status__in=['trash', 'duplicate']).order_by('-id')

        el_id = self.request.GET.get('id')

        offer_id = self.request.GET.get('offer_id')
        status = self.request.GET.get('lead_status')
        domain_name = self.request.GET.get('domain_name')
        name = self.request.GET.get('name')
        processing_status = self.request.GET.get('precessing_status')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        geo = self.request.GET.get("geo")
        phone_number = self.request.GET.get("phone_number")


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

        if geo:
            query = Q()
            for el in geo.split():
                query |= Q(geo__icontains=el)  # Ищем по каждому слову

            # Применяем фильтр с использованием Q-объекта
            queryset = queryset.filter(query)

        if phone_number:
            queryset = queryset.filter(phone=phone_number)

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

            if new_processing_status:
                # Если это изменение статуса обработки
                lead = get_object_or_404(LeadWall, id=lead_id)
                offer_web = OfferWebmaster.objects.get(id=lead.offer_webmaster_id)
                offer = Offer.objects.get(id=offer_web.offer_id)

                if lead.status in ["on_hold", "cancelled"]:
                    lead.processing_status = new_processing_status

                    if (new_processing_status in offer.validation_data_lead) or new_processing_status in ["expired"]:
                        lead.status = 'paid'
                        lead.offer_webmaster.offer.partner_card.deposit -= lead.offer_webmaster.offer.offer_price
                        lead.offer_webmaster.offer.partner_card.save()

                    if new_processing_status in offer.validation_data_web:
                        lead.offer_webmaster.webmaster.balance += lead.offer_webmaster.offer.lead_price
                        lead.offer_webmaster.webmaster.save()

                    if new_processing_status in ['rejected', 'trash', 'duplicate']:
                        lead.status = 'cancelled'

                    lead.save()
                    return JsonResponse({'success': True})
                else:
                    return JsonResponse({'success': False, 'message': 'Нельзя изменить на этот статус.'})

        return JsonResponse({'success': False, 'message': 'Неверный запрос или метод запроса не является AJAX.'},
                            status=400)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Передаем форматированные строки дат в шаблон
        get_date = self.request.GET.get('date')

        if get_date:
            get_date = get_date.split(' - ')
            context['start_date'] = get_date[0].replace('/', '-')
            context['end_date'] = get_date[1].replace('/', '-')
        else:
            today = datetime.now()
            week_ago = today - timedelta(days=7)
            context['start_date'] = week_ago.strftime('%m/%d/%Y')
            context['end_date'] = today.strftime('%m/%d/%Y')

        context['offers'] = Offer.objects.filter(partner_card__advertiser=self.request.user.advertiser)

        # Calculate date range
        return context


class AdminLeadsView(LoginRequiredMixin, ListView):
    model = LeadWall
    template_name = 'leads/admin_leads.html'
    context_object_name = 'leads'
    paginate_by = 10

    def get_queryset(self):
        advertiser = get_object_or_404(Advertiser, user=self.request.user)
        queryset = LeadWall.objects.all().order_by('-id')

        el_id = self.request.GET.get('id')

        offer_id = self.request.GET.get('offer_id')
        status = self.request.GET.get('lead_status')
        domain_name = self.request.GET.get('domain_name')
        name = self.request.GET.get('name')
        processing_status = self.request.GET.get('precessing_status')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        sub_filters = {f"sub_{i}": self.request.GET.get(f"sub_{i}") for i in range(1, 6)}
        geo = self.request.GET.get("geo")
        phone_number = self.request.GET.get("phone_number")


        if el_id:
            queryset = queryset.filter(id=el_id)

        if offer_id:
            queryset = queryset.filter(offer_webmaster__offer__id=offer_id)

        if domain_name:
            queryset = queryset.filter(domain=domain_name)

        if name:
            queryset = queryset.filter(name__icontains=name)

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

        if geo:
            query = Q()
            for el in geo.split():
                query |= Q(geo__icontains=el)  # Ищем по каждому слову

            # Применяем фильтр с использованием Q-объекта
            queryset = queryset.filter(query)

        if phone_number:
            queryset = queryset.filter(phone__icontains=phone_number)

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

            if new_processing_status:
                # Если это изменение статуса обработки
                lead = get_object_or_404(LeadWall, id=lead_id)
                offer_web = OfferWebmaster.objects.get(id=lead.offer_webmaster_id)
                offer = Offer.objects.get(id=offer_web.offer_id)

                if lead.status in ["on_hold", "cancelled"]:
                    lead.processing_status = new_processing_status
                    if (new_processing_status in offer.validation_data_lead) or new_processing_status in ["expired"]:
                        lead.status = 'paid'
                        lead.offer_webmaster.offer.partner_card.deposit -= lead.offer_webmaster.offer.offer_price
                        lead.offer_webmaster.offer.partner_card.save()
                    else:
                        lead.status = 'on_hold'

                    if new_processing_status in offer.validation_data_web:
                        lead.offer_webmaster.webmaster.balance += lead.offer_webmaster.offer.lead_price
                        lead.offer_webmaster.webmaster.save()

                    if new_processing_status in ['rejected', 'trash', 'duplicate']:
                        lead.status = 'cancelled'


                    lead.save()
                    return JsonResponse({'success': True})
                else:
                    return JsonResponse({'success': False, 'message': 'Нельзя изменить на этот статус.'})

        return JsonResponse({'success': False, 'message': 'Неверный запрос или метод запроса не является AJAX.'},
                            status=400)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Передаем форматированные строки дат в шаблон
        get_date = self.request.GET.get('date')

        if get_date:
            get_date = get_date.split(' - ')
            context['start_date'] = get_date[0].replace('/', '-')
            context['end_date'] = get_date[1].replace('/', '-')
        else:
            today = datetime.now()
            week_ago = today - timedelta(days=7)
            context['start_date'] = week_ago.strftime('%m/%d/%Y')
            context['end_date'] = today.strftime('%m/%d/%Y')

        context['offers'] = Offer.objects.filter(partner_card__advertiser=self.request.user.advertiser)

        # Calculate date range
        return context


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
        get_date = self.request.GET.get('date')

        if get_date:
            get_date = get_date.split(' - ')
            start_date = get_date[0].replace('/', '-')
            end_date = get_date[1].replace('/', '-')
        else:
            start_date = None
            end_date = None

        offer_id = self.request.GET.get('offer_id')
        enter_type = self.request.GET.get('enter_type')

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

        if enter_type == "by_offer":
            # Группировка по офферам за всё время
            offer_stats = leads.values('offer_webmaster__offer__name', 'offer_webmaster__offer__id').annotate(
                unique_leads=Count('id', distinct=True),
                approved_leads=Count('id', filter=Q(status='paid')),
                new_leads=Count('id', filter=Q(status='on_hold')),
                rejected_leads=Count('id', filter=Q(status='cancelled')),
                trash_leads=Count('id', filter=Q(processing_status='trash')),
                duplicate_leads=Count('id', filter=Q(processing_status='duplicate')),
                accepted_leads=Count('id', filter=Q(status__in=['visit', 'appointment', 'paid', 'expired'])),
                earned=Sum('offer_webmaster__offer__lead_price',
                           filter=Q(status__in=['visit', 'appointment', 'paid', 'expired'])),
                on_hold=Sum('offer_webmaster__offer__lead_price',
                           filter=Q(status="on_hold")),
                sum_konv=Count('id', filter=Q(status__in=['visit', 'appointment', 'paid', 'expired']))
            ).order_by('offer_webmaster__offer__name')

            for stat in offer_stats:
                offer_id = stat['offer_webmaster__offer__id']
                total_clicks = clicks_dict.get(offer_id, 0)
                lead_price = Offer.objects.get(id=offer_id).lead_price  # Получение стоимости лида из оффера
                stat['lead_price'] = lead_price
                stat['total_income'] = stat['approved_leads'] * lead_price  # Расчет дохода
                stat['approve_percent'] = (stat['approved_leads'] / stat['unique_leads'] * 100) if stat['unique_leads'] > 0 else 0
                stat['conversion_rate'] = (stat['unique_leads'] / total_clicks * 100) if total_clicks > 0 else 0
                stat['epc'] = (stat['total_income'] / total_clicks) if total_clicks > 0 else 0

        elif enter_type == "by_month":

            offer_stats = (
                leads
                .annotate(month=TruncMonth('update_at__date'))
                .values('month')  # Группируем по месяцам
                .annotate(
                    unique_leads=Count('id', distinct=True),
                    approved_leads=Count('id', filter=Q(status='paid')),
                    new_leads=Count('id', filter=Q(status='on_hold')),
                    rejected_leads=Count('id', filter=Q(status='cancelled')),
                    trash_leads=Count('id', filter=Q(processing_status='trash')),
                    duplicate_leads=Count('id', filter=Q(processing_status='duplicate')),
                    accepted_leads=Count('id', filter=Q(status__in=['visit', 'appointment', 'paid', 'expired'])),
                    earned=Sum('offer_webmaster__offer__lead_price',
                               filter=Q(status__in=['visit', 'appointment', 'paid', 'expired'])),
                    on_hold=Sum('offer_webmaster__offer__lead_price', filter=Q(status='on_hold')),
                    sum_konv=Count('id', filter=Q(
                        status__in=['trash', 'duplicate', 'paid', 'on_hold', 'visit', 'appointment', 'expired']))
                )
                .order_by('month')
            )

            for stat in offer_stats:
                total_clicks = clicks.filter(created_at__date=stat['month']).count()

                stat['month'] = stat['month'].strftime('%B - %Y')
                stat['approve_percent'] = (stat['approved_leads'] / stat['unique_leads'] * 100) if stat[
                                                                                                       'unique_leads'] > 0 else 0
                stat['conversion_rate'] = (stat['unique_leads'] / total_clicks * 100) if total_clicks > 0 else 0
                stat['epc'] = (stat['earned'] / total_clicks) if total_clicks > 0 else 0


        elif enter_type == 'by_hour':
            # Группировка по часам
            offer_stats = leads.values('created_at__date', 'offer_webmaster__offer__id').annotate(
                unique_leads=Count('id', distinct=True),
                approved_leads=Count('id', filter=Q(status='paid')),
                new_leads=Count('id', filter=Q(status='on_hold')),
                rejected_leads=Count('id', filter=Q(status='cancelled')),
                trash_leads=Count('id', filter=Q(processing_status='trash')),
                duplicate_leads=Count('id', filter=Q(processing_status='duplicate')),
                accepted_leads=Count('id', filter=Q(status__in=['visit', 'appointment', 'paid', 'expired'])),
                earned=Sum('offer_webmaster__offer__lead_price',
                           filter=Q(status__in=['visit', 'appointment', 'paid', 'expired'])),
                on_hold=Sum('offer_webmaster__offer__lead_price',
                            filter=Q(status="on_hold")),
            ).order_by('created_at__hour')

            for stat in offer_stats:
                # Здесь не используется ключ 'offer_webmaster__offer__id', поскольку группировка идет по дате
                total_clicks = clicks.filter(created_at__date=stat['created_at__date']).count()
                lead_price = offers.aggregate(Sum('offer__lead_price'))['offer__lead_price__sum'] or 0
                stat['lead_price'] = Offer.objects.get(id=stat['offer_webmaster__offer__id']).lead_price

                stat['total_income'] = stat['approved_leads'] * lead_price  # Расчет дохода
                stat['approve_percent'] = (stat['approved_leads'] / stat['unique_leads'] * 100) if stat[
                                                                                                       'unique_leads'] > 0 else 0
                stat['conversion_rate'] = (stat['unique_leads'] / total_clicks * 100) if total_clicks > 0 else 0
                stat['epc'] = (stat['total_income'] / total_clicks) if total_clicks > 0 else 0

        else:
            # Группировка по дате
            offer_stats = leads.values('created_at__date', 'offer_webmaster__offer__id').annotate(
                unique_leads=Count('id', distinct=True),
                approved_leads=Count('id', filter=Q(status='paid')),
                new_leads=Count('id', filter=Q(status='on_hold')),
                rejected_leads=Count('id', filter=Q(status='cancelled')),
                trash_leads=Count('id', filter=Q(processing_status='trash')),
                duplicate_leads=Count('id', filter=Q(processing_status='duplicate')),
                accepted_leads=Count('id', filter=Q(status__in=['visit', 'appointment', 'paid', 'expired'])),
                earned=Sum('offer_webmaster__offer__lead_price',
                           filter=Q(status__in=['visit', 'appointment', 'paid', 'expired'])),
                on_hold=Sum('offer_webmaster__offer__lead_price',
                            filter=Q(status="on_hold")),
            ).order_by('created_at__date')

            for stat in offer_stats:
                # Здесь не используется ключ 'offer_webmaster__offer__id', поскольку группировка идет по дате
                total_clicks = clicks.filter(created_at__date=stat['created_at__date']).count()
                lead_price = offers.aggregate(Sum('offer__lead_price'))['offer__lead_price__sum'] or 0
                stat['lead_price'] = Offer.objects.get(id=stat['offer_webmaster__offer__id']).lead_price

                stat['total_income'] = stat['approved_leads'] * lead_price  # Расчет дохода
                stat['approve_percent'] = (stat['approved_leads'] / stat['unique_leads'] * 100) if stat['unique_leads'] > 0 else 0
                stat['conversion_rate'] = (stat['unique_leads'] / total_clicks * 100) if total_clicks > 0 else 0
                stat['epc'] = (stat['total_income'] / total_clicks) if total_clicks > 0 else 0

        return offer_stats

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Передаем форматированные строки дат в шаблон
        get_date = self.request.GET.get('date')

        if get_date:
            get_date = get_date.split(' - ')
            context['start_date'] = get_date[0].replace('/', '-')
            context['end_date'] = get_date[1].replace('/', '-')
        else:
            today = datetime.now()
            week_ago = today - timedelta(days=7)
            context['start_date'] = week_ago.strftime('%m/%d/%Y')
            context['end_date'] = today.strftime('%m/%d/%Y')
        context['offers'] = OfferWebmaster.objects.filter(webmaster=self.request.user.webmaster)

        # Calculate date range
        return context

class WebmasterFinancialStatisticsView(LoginRequiredMixin, View):
    template_name = 'statistics/webmaster_financial_statistics.html'
    paginate_by = 50

    def get(self, request, *args, **kwargs):
        webmaster = get_object_or_404(Webmaster, user=request.user)
        offers = Offer.objects.filter(webmaster_links__webmaster=webmaster)

        get_date = self.request.GET.get('date')

        if get_date:
            get_date = get_date.split(' - ')
            start_date = get_date[0].replace('/', '-')
            end_date = get_date[1].replace('/', '-')
        else:
            start_date = None
            end_date = None
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
            unique_leads=Count('id', distinct=True),
            accepted_leads=Count('id', filter=Q(status__in=['visit', 'appointment', 'paid', 'expired'])),
            earned=Sum('offer_webmaster__offer__lead_price', filter=Q(status__in=['visit', 'appointment', 'paid', 'expired'])),
            on_hold=Sum('offer_webmaster__offer__lead_price',
                        filter=Q(status="on_hold")),
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

        result = {
            "res_accepted_leads": sum([stat['accepted_leads'] for stat in financial_stats]),
            "res_earned": sum([int(stat['earned']) for stat in financial_stats if stat['earned']]),
            "res_hold": sum([int(stat['on_hold']) for stat in financial_stats if stat['on_hold']]),
            "res_total_lead: ": sum([int(stat['unique_leads']) for stat in financial_stats])
        }

        context = {
            'offers': offers,
            'financial_stats': financial_stats,
            'result': result
        }
        return render(request, self.template_name, context)


class AdvertiserOfferStatisticsView(LoginRequiredMixin, View):
    template_name = 'statistics/advertiser_offer_statistics.html'
    paginate_by = 50

    def get(self, request, *args, **kwargs):
        advertiser = get_object_or_404(Advertiser, user=request.user)
        offers = Offer.objects.filter(partner_card__advertiser=advertiser)
        print(offers)
        offer_web = OfferWebmaster.objects.filter(offer__partner_card__advertiser=advertiser)

        # Получение фильтров из запроса
        get_date = self.request.GET.get('date')

        if get_date:
            get_date = get_date.split(' - ')
            start_date = get_date[0].replace('/', '-')
            end_date = get_date[1].replace('/', '-')
        else:
            start_date = None
            end_date = None

        offer_id = request.GET.get('offer_id')
        enter_type = request.GET.get('enter_type')



        # Фильтрация по дате и офферам
        lead_filter = Q(offer_webmaster__in=offer_web)
        if start_date:
            lead_filter &= Q(created_at__gte=datetime.strptime(start_date, '%Y-%m-%d'))
        if end_date:
            lead_filter &= Q(created_at__lte=datetime.strptime(end_date, '%Y-%m-%d'))
        if offer_id:
            lead_filter &= Q(offer_webmaster__offer__id=offer_id)

        leads = LeadWall.objects.filter(lead_filter)

        clicks = Click.objects.filter(offer_webmaster__in=offer_web)
        if start_date:
            clicks = clicks.filter(created_at__gte=datetime.strptime(start_date, '%Y-%m-%d'))
        if end_date:
            clicks = clicks.filter(created_at__lte=datetime.strptime(end_date, '%Y-%m-%d'))
        if offer_id:
            clicks = clicks.filter(offer_webmaster__offer_id=offer_id)

        click_counts = clicks.values('offer_webmaster__offer__id').annotate(total_clicks=Count('id')).order_by()

        clicks_dict = {item['offer_webmaster__offer__id']: item['total_clicks'] for item in click_counts}

        if enter_type == 'by_days':
            # Статистика по дням
            offer_stats = leads.values('offer_webmaster__offer__name', 'offer_webmaster__offer__id', 'created_at__date').annotate(
                unique_leads=Count('id', distinct=True),
                approved_leads=Count('id', filter=Q(status__in=['visit', 'appointment', 'paid', 'expired'])),
                new_leads=Count('id', filter=Q(processing_status='new')),
                rejected_leads=Count('id', filter=Q(
                    processing_status__in=['no_response', 'callback', 'appointment', 'visit', 'trash', 'duplicate'])),
                paid=Sum('offer_webmaster__offer__offer_price',
                           filter=Q(status__in=['paid']))
            ).order_by('created_at')

            for stat in offer_stats:
                stat['approve_percent'] = (stat['approved_leads'] / stat['unique_leads'] * 100) if stat[
                                                                                                       'unique_leads'] > 0 else 0
        elif enter_type == "by_month":

            offer_stats = (
                leads
                .annotate(month=TruncMonth('create_at__date'))
                .values('month')  # Группируем по месяцам
                .annotate(
                    unique_leads=Count('id', distinct=True),
                    approved_leads=Count('id', filter=Q(status='paid')),
                    new_leads=Count('id', filter=Q(status='on_hold')),
                    rejected_leads=Count('id', filter=Q(status='cancelled')),
                    trash_leads=Count('id', filter=Q(processing_status='trash')),
                    duplicate_leads=Count('id', filter=Q(processing_status='duplicate')),
                    accepted_leads=Count('id', filter=Q(status__in=['visit', 'appointment', 'paid', 'expired'])),
                    earned=Sum('offer_webmaster__offer__lead_price',
                               filter=Q(status__in=['visit', 'appointment', 'paid', 'expired'])),
                    on_hold=Sum('offer_webmaster__offer__lead_price', filter=Q(status='on_hold')),
                    sum_konv=Count('id', filter=Q(
                        status__in=['trash', 'duplicate', 'paid', 'on_hold', 'visit', 'appointment', 'expired']))
                )
                .order_by('month')
            )

            for stat in offer_stats:
                total_clicks = clicks.filter(created_at__date=stat['month']).count()

                stat['month'] = stat['month'].strftime('%B - %Y')
                stat['approve_percent'] = (stat['approved_leads'] / stat['unique_leads'] * 100) if stat[
                                                                                                       'unique_leads'] > 0 else 0
                stat['conversion_rate'] = (stat['unique_leads'] / total_clicks * 100) if total_clicks > 0 else 0
                stat['epc'] = (stat['earned'] / total_clicks) if total_clicks > 0 else 0
        else:
            # Статистика по офферам
            offer_stats = leads.values('offer_webmaster__offer__name', 'offer_webmaster__offer__id',
                                       'offer_webmaster__offer__offer_price').annotate(
                unique_leads=Count('id', distinct=True),
                approved_leads=Count('id', filter=Q(status='paid')),
                new_leads=Count('id', filter=Q(status='on_hold')),
                rejected_leads=Count('id', filter=Q(status='cancelled')),
                duplicate_leads=Count('id', filter=Q(processing_status='duplicate')),
                accepted_leads=Count('id', filter=Q(status__in=['visit', 'appointment', 'paid', 'expired'])),
                earned=Sum('offer_webmaster__offer__offer_price',
                           filter=Q(status__in=['visit', 'appointment', 'paid', 'expired'])),
                on_hold=Sum('offer_webmaster__offer__offer_price',
                            filter=Q(status="on_hold")),
                sum_konv=Count('id', filter=Q(status__in=['visit', 'appointment', 'paid', 'expired'],
                                              processing_status__in=['trash', 'duplicate']))
            ).order_by('offer_webmaster__offer__name')

            for stat in offer_stats:
                total_clicks = clicks_dict.get(offer_id, 0)
                offer_price = offers.aggregate(Sum('offer_price'))['offer_price__sum'] or 0
                stat['approve_percent'] = (stat['approved_leads'] / stat['unique_leads'] * 100) if stat[
                                                                                                       'unique_leads'] > 0 else 0
                stat['total_income'] = stat['approved_leads'] * offer_price  # Расчет дохода
                stat['approve_percent'] = (stat['approved_leads'] / stat['unique_leads'] * 100) if stat[
                                                                                                       'unique_leads'] > 0 else 0
                stat['conversion_rate'] = (stat['unique_leads'] / total_clicks * 100) if total_clicks > 0 else 0
                stat['epc'] = (stat['total_income'] / total_clicks) if total_clicks > 0 else 0

        context = {
            'offers': offers,
            'offer_stats': offer_stats,
        }
        return render(request, self.template_name, context)



class AdminOfferStatisticsView(LoginRequiredMixin, View):
    template_name = 'statistics/admin_offer_statistics.html'
    paginate_by = 50

    def get(self, request, *args, **kwargs):
         # Получение фильтров из запроса


        get_date = self.request.GET.get('date')

        if get_date:
            get_date = get_date.split(' - ')
            start_date = get_date[0].replace('/', '-')
            end_date = get_date[1].replace('/', '-')
        else:
            start_date = None
            end_date = None

        offer_id = request.GET.get('offer_id')
        webmasters = request.GET.getlist('webmasters[]')
        # Фильтрация по дате и офферам
        partner_crd = PartnerCard.objects.all()

        all_data = []

        for card in partner_crd:
            if card.name not in all_data:

                per = {}

                offers = Offer.objects.filter(partner_card=card.id)

                offer_web = OfferWebmaster.objects.filter(offer_id__in=offers)

                lead_filter = Q(offer_webmaster__in=offer_web)
                if start_date:
                    lead_filter &= Q(created_at__gte=datetime.strptime(start_date, '%Y-%m-%d'))
                if end_date:
                    lead_filter &= Q(created_at__lte=datetime.strptime(end_date, '%Y-%m-%d'))
                if offer_id:
                    lead_filter &= Q(offer_webmaster__offer__id=offer_id)
                if webmasters:
                    lead_filter &= Q(offer_webmaster__webmaster_id__in=webmasters)
                leads = LeadWall.objects.filter(lead_filter)
                # Статистика по офферам

                offer_stats = leads.values('offer_webmaster__offer__name', 'offer_webmaster__offer__id',
                                           'offer_webmaster__webmaster__user__username', 'offer_webmaster__offer__offer_price',
                                           'offer_webmaster__offer__lead_price').annotate(
                    unique_leads=Count('id', distinct=True),
                    approved_leads=Count('id', filter=Q(status__in=['visit', 'appointment', 'paid', 'expired'])),
                    new_leads=Count('id', filter=Q(processing_status='new')),
                    rejected_leads=Count('id', filter=Q(
                        processing_status__in=['no_response', 'callback', 'appointment', 'visit', 'trash',
                                               'duplicate'])),
                    accepted_leads=Count('id', filter=Q(status__in=['visit', 'appointment', 'paid', 'expired'])),
                    on_hold=Sum('offer_webmaster__offer__offer_price',
                                filter=Q(status="on_hold")),
                    earned_offer=Sum('offer_webmaster__offer__offer_price',
                               filter=Q(status__in=['visit', 'appointment', 'paid', 'expired'])),
                    earned_web=Sum('offer_webmaster__offer__lead_price',
                                     filter=Q(status__in=['visit', 'appointment', 'paid', 'expired'])),
                ).order_by('offer_webmaster__offer__id')

                general_stat = {
                    'unique_leads_sum': 0,
                    'approved_leads_sum': 0,
                    'earned_advertiser_sum': 0,
                    'hold_sum': 0
                }

                for stat in offer_stats:
                    stat['approve_percent'] = round((stat['approved_leads'] / stat['unique_leads'] * 100) if stat[
                                                                                                           'unique_leads'] > 0 else 0, 2)

                    if stat['earned_offer']:
                        earned_offer = float(stat['earned_offer'])
                        stat['earned_offer'] =float(stat['earned_offer'])
                    else:
                        earned_offer= 0

                    if stat['earned_web']:
                        earned_web = float(stat['earned_web'])
                        stat['earned_web'] = float(stat['earned_web'])
                    else:
                        earned_web= 0

                    stat['earned_advertiser'] = earned_offer - earned_web

                    offer_price = 0
                    if stat['offer_webmaster__offer__offer_price']:
                        offer_price = float(stat['offer_webmaster__offer__offer_price'])

                    lead_price = 0
                    if stat['offer_webmaster__offer__lead_price']:
                        lead_price = float(stat['offer_webmaster__offer__lead_price'])

                    on_hold = 0
                    if stat['on_hold']:
                        on_hold = earned_offer - earned_web
                        stat['on_hold'] = on_hold
                    else:
                        stat['on_hold'] = 0

                    general_stat['unique_leads_sum'] += stat['unique_leads']
                    general_stat['approved_leads_sum'] += stat['approved_leads']
                    general_stat['earned_advertiser_sum'] += earned_offer - earned_web
                    general_stat['hold_sum'] += on_hold


                per['offer_stats'] = offer_stats
                per['name'] = card.name
                per['general_stats'] = general_stat
                all_data.append(per)


        webmasters = OfferWebmaster.objects.values("webmaster__user__username", 'webmaster_id').distinct()

        context = {
            'all_data': all_data,
            'partner_cards': partner_crd,
            'webmasters': webmasters,
            'select_webmasters': self.request.GET.getlist('webmasters[]'),
            'offers': Offer.objects.all()
        }

        return render(request, self.template_name, context)


class AdvertiserFinancialStatisticsView(LoginRequiredMixin, View):
    template_name = 'statistics/advertiser_financial_statistics.html'
    paginate_by = 50

    def get(self, request, *args, **kwargs):
        advertiser = get_object_or_404(Advertiser, user=request.user)
        if request.user.is_superuser:
            offers = Offer.objects.all()
        else:
            offers = Offer.objects.filter(partner_card__advertiser=advertiser)

        get_date = self.request.GET.get('date')

        if get_date:
            get_date = get_date.split(' - ')
            start_date = get_date[0].replace('/', '-')
            end_date = get_date[1].replace('/', '-')
        else:
            start_date = None
            end_date = None

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
            unique_leads=Count('id', distinct=True),
            accepted_leads=Count('id', filter=Q(status__in=['visit', 'appointment', 'paid', 'expired'])),
            spent=Sum('offer_webmaster__offer__offer_price', filter=Q(status__in=['visit', 'appointment', 'paid', 'expired'])),
            on_hold=Sum('offer_webmaster__offer__offer_price',
                        filter=Q(status="on_hold")),

        ).order_by('offer_webmaster__offer__name')

        result = {
            "res_accepted_leads": sum([stat['accepted_leads'] for stat in financial_stats]),
            "res_spent": sum([int(stat['spent']) for stat in financial_stats if stat['spent']]),
        }

        context = {
            'offers': offers,
            'financial_stats': financial_stats,
            'result': result
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


@csrf_exempt  # Отключаем проверку CSRF, так как запросы идут от внешнего сервиса
def firstlead_postback(request):
    if request.method == 'POST':
        try:
            # Парсим данные из запроса
            data = json.loads(request.body)

            # Получаем необходимые параметры
            click_id = data.get('click_id')
            conversion_id = data.get('conversion_id')
            revenue = data.get('revenue')
            status = data.get('status')

            # Логика обработки данных
            if status == 'success':
                # Например, сохраняем данные в базу
                # (замените "PostbackModel" на вашу модель)
                from .models import PostbackModel
                PostbackModel.objects.create(
                    click_id=click_id,
                    conversion_id=conversion_id,
                    revenue=revenue,
                    status=status,
                )

            # Возвращаем успешный ответ
            return JsonResponse({'message': 'Postback received successfully'}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)