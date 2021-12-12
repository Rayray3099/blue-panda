from django import forms
from .models import Invoice, InvoiceNotes

import datetime
import requests


class InvoiceNoteForm(forms.ModelForm):

    notes = forms.CharField(widget=forms.Textarea(attrs={'cols':100, 'rows': 3, 'style': 'width: 100%',}))

    class Meta:
        model = InvoiceNotes
        fields = (
            'notes',
            )
