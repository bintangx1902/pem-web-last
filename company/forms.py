from django import forms
from .models import *
from django.apps import apps

Complaint = apps.get_model('client_side.Complaint')
JoinUs = apps.get_model('client_side.JoinUs')


class OpenJobForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['tech_quota', 'due_date', 'needed_tools']

        widgets = {
            'due_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local'
            })
        }


class GroundReportForm(forms.ModelForm):
    class Meta:
        model = GroundReport
        fields = ['file', 'case']


class SetGroundPriceForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ('ground_price',)

        widgets = {
            'ground_price': forms.NumberInput(attrs={'required': True})
        }
