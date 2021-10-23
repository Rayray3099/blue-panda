from django import forms
from .models import Quote, QuoteNotes, QuoteReviews
from leads.models import User, Lead
from products.models import Product

from django.forms.models import inlineformset_factory

import datetime
import requests

class QuoteModelForm(forms.ModelForm):

    t_stamp = datetime.datetime.now()
    t_stamp.strftime('%m%d%Y')
    
    class Meta:
        model = Quote
        fields = (
            'quote_id',
            'customer',
            'products',
            'multi_select',
            'active',
            )

    quote_id = str(t_stamp)
    products = forms.ModelMultipleChoiceField(
        queryset=Product.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'cols': 5,}))
            
    def __init__(self, *args, **kwargs):
        super(QuoteModelForm, self).__init__(*args, **kwargs)
        self.fields['quote_id'].required = True
        self.fields['customer'].required = True
        self.fields['products'].required = True
        self.fields['multi_select'].required = False
        self.fields['active'].required = False

QuoteFormset = inlineformset_factory(
    Product,
    Quote,
    fields=('products', ),
    extra=2,
    can_delete=True,
)

class QuoteNoteForm(forms.ModelForm):

    notes = forms.CharField(widget=forms.Textarea(attrs={'cols':100, 'rows': 3, 'style': 'width: 100%',}))

    class Meta:
        model = QuoteNotes
        fields = (
            'notes',
            )

class QuoteReviewForm(forms.ModelForm):
    FIVE_STARS = ((1, '1 star',),
                  (2, '2 stars',),
                  (3, '3 stars',),
                  (4, '4 stars',),
                  (5, '5 stars',))

    stars = forms.ChoiceField(widget=forms.RadioSelect, choices=FIVE_STARS)
    reviews = forms.CharField(widget=forms.Textarea(attrs={'cols':100, 'rows': 3, 'style': 'width: 100%',}))
    
    class Meta:
        model = QuoteReviews
        fields = (
            'stars',
            'reviews',
            )
