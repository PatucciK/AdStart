from django import forms
from .models import Offer


class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ['logo', 'name', 'inn', 'working_hours', 'service_description', 'geo', 'public_status', 'lead_price']
        widgets = {
            'lead_price': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
        }
        labels = {
            'logo': 'Логотип компании (для размещения на рекламных сайтах)',
            'name': 'Наименование оффера (это название будут видеть веб-мастера)',
            'inn': 'ИНН (для размещения на рекламных сайтах)',
            'working_hours': 'Режим работы колл-центра',
            'service_description': 'Описание услуг по офферу (опишите всю полезную информацию для веб-мастера)',
            'geo': 'Гео (опишите расположение (страна, город, регион), откуда принимаются лиды)',
            'public_status': 'Статус публичности (при закрытом статусе - цену за лида и подбор вебмастера назначает менеджер,'
                              ' при публичном статусе - цену за лида назначаете вы, все одобренные вебмастера могут принять оффер)',
            'lead_price': 'Цена за лид, руб',
        }


    def __init__(self, *args, **kwargs):
        super(OfferForm, self).__init__(*args, **kwargs)
        self.fields['lead_price'].required = False
        self.fields['public_status'].help_text = "При публичном статусе заказ могут принять все одобренные вебмастера. Цену за лида нельзя будет поменять. При закрытом статусе - цену за лида назначает менеджер."

    def clean(self):
        cleaned_data = super().clean()
        public_status = cleaned_data.get('public_status')
        lead_price = cleaned_data.get('lead_price')

        if public_status == 'public' and not lead_price:
            self.add_error('lead_price', 'При публичном статусе нужно указать цену за лид.')

        if public_status == 'private':
            cleaned_data['lead_price'] = None  # Администратор назначает цену

        return cleaned_data
