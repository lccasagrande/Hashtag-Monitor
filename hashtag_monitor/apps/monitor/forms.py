
from django import forms
from django.core.exceptions import ValidationError

from .models import *


class HashtagForm(forms.ModelForm):
    class Meta:
        model = Hashtag
        fields = ['name']
        widgets = {'name': forms.TextInput(
            attrs={'class': 'form-control', 'required': True})}
        labels = {'name': "What're you looking?"}
        error_messages={'unique':"This hashtag has already been added."}
