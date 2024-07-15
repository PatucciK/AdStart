from django import forms
from .models import Offer

class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = [
            'status', 'logo', 'name', 'legal_name', 'inn', 'contract_number', 'contract_date',
            'license', 'website', 'legal_address', 'actual_addresses', 'working_hours', 'service_description',
            'geo', 'lead_validity', 'landing_page', 'postback_documentation', 'lead_price'
        ]
        labels = {
            'status': 'Актуальность',
            'logo': 'Логотип',
            'name': 'Наименование',
            'legal_name': 'Наименование Юр. лица',
            'inn': 'ИНН',
            'contract_number': 'Номер Договора',
            'contract_date': 'Дата Договора',
            'license': 'Лицензия',
            'website': 'Ссылка на официальный сайт',
            'legal_address': 'Юридический адрес',
            'actual_addresses': 'Фактический адрес',
            'working_hours': 'Режим работы',
            'service_description': 'Описание услуг по офферу',
            'geo': 'ГЕО',
            'lead_validity': 'Валидность лида',
            'landing_page': 'Ссылка на посадку',
            'postback_documentation': 'Документация по отправке постзапросов',
            'lead_price': 'Цена за лид'
        }
