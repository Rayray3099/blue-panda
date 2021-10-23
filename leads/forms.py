from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UsernameField
from .models import Lead, LeadNotes, LeadReviews 

User = get_user_model()

class LeadModelForm(forms.ModelForm):
    
    class Meta:
        model = Lead
        fields = (
            'first_name',
            'last_name',
            'address',
            'city',
            'province',
            'country',
            'zip_code',
            'home_phone',
            'work_phone',
            'email',
            'agent',
            'multi_select',
            'active',
            )
        
    def __init__(self, *args, **kwargs):
        super(LeadModelForm, self).__init__(*args, **kwargs)
        self.fields['address'].required = False
        self.fields['city'].required = False
        self.fields['province'].required = False
        self.fields['country'].required = False
        self.fields['zip_code'].required = False
        self.fields['work_phone'].required = False
        self.fields['email'].required = False
        self.fields['multi_select'].required = False
        self.fields['active'].required = False

class LeadNoteForm(forms.ModelForm):

    notes = forms.CharField(widget=forms.Textarea(attrs={'cols':100, 'rows': 3, 'style': 'width: 100%',}))

    class Meta:
        model = LeadNotes
        fields = (
            'notes',
            )

class LeadReviewForm(forms.ModelForm):
    FIVE_STARS = ((1, '1 star',),
                  (2, '2 stars',),
                  (3, '3 stars',),
                  (4, '4 stars',),
                  (5, '5 stars',))

    stars = forms.ChoiceField(widget=forms.RadioSelect, choices=FIVE_STARS)
    reviews = forms.CharField(widget=forms.Textarea(attrs={'cols':100, 'rows': 3, 'style': 'width: 100%',}))
    
    class Meta:
        model = LeadReviews
        fields = (
            'stars',
            'reviews',
            )

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username",)
        field_classes = {'username': UsernameField}
    
