from django import forms
from .models import PartnerCard


class PartnerCardForm(forms.ModelForm):
    class Meta:
        model = PartnerCard
        fields = [
            'logo', 'name', 'legal_name', 'license', 'website', 'legal_address',
            'actual_addresses', 'company_details', 'contracts', 'main_phone'
        ]

        labels = {
            'logo': 'Логотип',
            'name': 'Наименование',
            'legal_name': 'Наименование юридического лица',
            'license': 'Лицензия',
            'website': 'Ссылка на официальный сайт',
            'legal_address': 'Юридический адрес',
            'actual_addresses': 'Фактический адрес',
            'company_details': 'Реквизиты компании',
            'contracts': 'Договор, акты, доп. соглашения для понимания рекламного кейса',
            'main_phone': 'Телефон основной',
        }
