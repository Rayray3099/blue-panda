from django import forms
from .models import Quote, QuoteNotes, QuoteProducts
from leads.models import User, Lead
from products.models import Product

import datetime
import requests

class QuoteModelForm(forms.ModelForm):
    
    class Meta:
        model = Quote
        fields = (
            'customer',
            'active',            
            )
            
    def __init__(self, *args, **kwargs):
        super(QuoteModelForm, self).__init__(*args, **kwargs)
        
        self.fields['active'].required = False


class QuoteProductForm(forms.ModelForm):

    class Meta:
        model = QuoteProducts
        fields = (
            'product_select',
            'product_quantity',
            'quote_status',
            )

    def __init__(self, *args, **kwargs):
        super(QuoteProductForm, self).__init__(*args, **kwargs)

        self.fields['product_select'] = forms.ModelChoiceField(
              widget=forms.Select,   
              queryset=Product.objects.all())


class QuoteNoteForm(forms.ModelForm):

    notes = forms.CharField(widget=forms.Textarea(attrs={'cols':100, 'rows': 3, 'style': 'width: 100%',}))

    class Meta:
        model = QuoteNotes
        fields = (
            'notes',
            )
