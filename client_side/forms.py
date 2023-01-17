from django import forms
from .models import *
from django.apps import apps

UserProfile = apps.get_model('company.UserProfile')


class CreateComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['title', 'messages', 'address']


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['wa_number', 'nik']


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

        widgets = {
            'first_name': forms.TextInput(attrs={'required': True}),
            'last_name': forms.TextInput(attrs={'required': True}),
            'email': forms.TextInput(attrs={'required': True}),
        }


class JoinUsForms(forms.ModelForm):
    class Meta:
        model = JoinUs
        fields = ['foto_ktp', 'desc']
