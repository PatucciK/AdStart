from django import forms
from .models import SiteArchive

class SiteArchiveForm(forms.ModelForm):
    class Meta:
        model = SiteArchive
        fields = ['name', 'offer', 'category', 'archive']