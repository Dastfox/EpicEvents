from django import forms
from .models import Client, Event, Contract


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = "__all__"


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = "__all__"


class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = "__all__"
