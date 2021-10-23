from django import forms
from .models import Product, ProductNotes, ProductReviews
import requests

class ProductModelForm(forms.ModelForm):

    product_description = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Product Description', 'cols':80, 'rows': 4, 'style': 'width: 100%',}))
    inventory_count = forms.FloatField(widget=forms.TextInput(attrs={'placeholder': 'Inventory Count', 'style': 'width: 100%',}))
    sell_price = forms.FloatField(widget=forms.TextInput(attrs={'placeholder': 'Sell Price', 'style': 'width: 100%',}))
    cost_price = forms.FloatField(widget=forms.TextInput(attrs={'placeholder': 'Cost Price', 'style': 'width: 100%',}))
    product_length = forms.FloatField(widget=forms.TextInput(attrs={'placeholder': 'Length', 'style': 'width: 100%',}))   
    product_width = forms.FloatField(widget=forms.TextInput(attrs={'placeholder': 'Width', 'style': 'width: 100%',}))
    product_height = forms.FloatField(widget=forms.TextInput(attrs={'placeholder': 'Height', 'style': 'width: 100%',}))
    product_volume = forms.FloatField(widget=forms.TextInput(attrs={'placeholder': 'Volume', 'style': 'width: 100%',}))
    product_weight = forms.FloatField(widget=forms.TextInput(attrs={'placeholder': 'Weight', 'style': 'width: 100%',}))
    product_image_one = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Image URL',}))
    product_image_two = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Image URL',}))
    product_image_three = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Image URL',}))
    product_image_four = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Image URL',}))
    product_image_five = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Image URL',}))
    
    class Meta:
        model = Product
        fields = (
            'product_code',
            'brand_name',
            'brand_family',
            'internal_code',
            'upc',
            'part_number',
            'product_title',
            'product_description',
            'sell_price',
            'cost_price',
            'inventory_count',
            'product_material',
            'product_color',
            'product_length',
            'product_width',
            'product_height',
            'product_volume',
            'product_weight',
            'product_image_one',
            'product_image_two',
            'product_image_three',
            'product_image_four',
            'product_image_five',
            'active',
            )

    def clean_product_code(self, *args, **kwargs):
        product_code = self.cleaned_data.get("product_code")
               
        if len(product_code) < 4:
            raise forms.ValidationError("Product Code is too short")       
        return product_code

    def clean_product_title(self, *args, **kwargs):
        product_title = self.cleaned_data.get("product_title")
               
        if len(product_title) < 10:
            raise forms.ValidationError("Product Title is too short")       
        return product_title

    def clean_product_image_url(self, *args, **kwargs):
        image_formats = ("image/png", "image/jpeg", "image/jpg", "image/gif")
        product_image_one = self.cleaned_data.get("product_image_one")
        product_image_two = self.cleaned_data.get("product_image_two")
        product_image_three = self.cleaned_data.get("product_image_three")
        product_image_four = self.cleaned_data.get("product_image_four")
        product_image_five = self.cleaned_data.get("product_image_five")

        if not product_image_one:
            pass
        else:
            request_test = requests.head(product_image_one)
               
            if request_test.headers["content-type"] not in image_formats:
                raise forms.ValidationError("This is not a valid image")       
            return product_image_one

        if not product_image_two:
            pass
        else:
            request_test = requests.head(product_image_two)
               
            if request_test.headers["content-type"] not in image_formats:
                raise forms.ValidationError("This is not a valid image")       
            return product_image_two

        if not product_image_three:
            pass
        else:
            request_test = requests.head(product_image_three)
               
            if request_test.headers["content-type"] not in image_formats:
                raise forms.ValidationError("This is not a valid image")       
            return product_image_three
        
        if not product_image_four:
            pass
        else:
            request_test = requests.head(product_image_four)
               
            if request_test.headers["content-type"] not in image_formats:
                raise forms.ValidationError("This is not a valid image")       
            return product_image_four

        if not product_image_five:
            pass
        else:
            request_test = requests.head(product_image_five)
               
            if request_test.headers["content-type"] not in image_formats:
                raise forms.ValidationError("This is not a valid image")       
            return product_image_five
        
    def __init__(self, *args, **kwargs):
        super(ProductModelForm, self).__init__(*args, **kwargs)
        self.fields['brand_name'].required = False
        self.fields['brand_family'].required = False
        self.fields['internal_code'].required = False
        self.fields['upc'].required = False
        self.fields['part_number'].required = False
        self.fields['product_description'].required = False
        self.fields['cost_price'].required = False
        self.fields['inventory_count'].required = False
        self.fields['product_material'].required = False
        self.fields['product_color'].required = False
        self.fields['product_length'].required = False
        self.fields['product_width'].required = False
        self.fields['product_height'].required = False
        self.fields['product_volume'].required = False
        self.fields['product_weight'].required = False
        self.fields['product_image_one'].required = False
        self.fields['product_image_two'].required = False
        self.fields['product_image_three'].required = False
        self.fields['product_image_four'].required = False
        self.fields['product_image_five'].required = False
        self.fields['active'].required = False

class ProductNoteForm(forms.ModelForm):

    notes = forms.CharField(widget=forms.Textarea(attrs={'cols':100, 'rows': 3, 'style': 'width: 100%',}))

    class Meta:
        model = ProductNotes
        fields = (
            'notes',
            )

class ProductReviewForm(forms.ModelForm):
    FIVE_STARS = ((1, '1 star',),
                  (2, '2 stars',),
                  (3, '3 stars',),
                  (4, '4 stars',),
                  (5, '5 stars',))

    stars = forms.ChoiceField(widget=forms.RadioSelect, choices=FIVE_STARS)
    reviews = forms.CharField(widget=forms.Textarea(attrs={'cols':100, 'rows': 3, 'style': 'width: 100%',}))
    
    class Meta:
        model = ProductReviews
        fields = (
            'stars',
            'reviews',
            )
