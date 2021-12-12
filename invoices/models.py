from django.db import models
from django.utils import timezone
from django.db.models import Avg
from leads.models import User, Lead
from products.models import Product
from quotes.models import Quote, QuoteProducts

import time
import datetime

def create_id():
    now = datetime.datetime.now()
    return str(now.year)+str(now.month)+str(now.day)+str(now.hour)+str(now.minute)+str(now.second)+str("-")+str(now.microsecond)

def current_milli_time():
    return round(time.time() * 1000)

class Invoice(models.Model):

    invoice_id = models.CharField(max_length=64, default=create_id)
    quote = models.ForeignKey(Quote, on_delete=models.PROTECT)
    date_added = models.DateTimeField(blank=True, null=True, default=timezone.now)

    invoice_first_name = models.CharField(max_length=64)
    invoice_last_name = models.CharField(max_length=64)
    invoice_address = models.CharField(max_length=128)
    invoice_zip_code = models.CharField(max_length=20)
    invoice_home_phone = models.CharField(max_length=20)

    #invoice_product_select = models.ForeignKey(QuoteProducts, on_delete=models.PROTECT)
    invoice_quote_key = models.IntegerField(default=1)
    invoice_product_quantity = models.IntegerField(default=1)
    invoice_product_price = models.FloatField(default=0)
    
    def __str__(self):
        return f"{self.quote}"

class InvoiceNotes(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date_added = models.DateTimeField(blank=True, null=True, default=timezone.now)
    notes = models.CharField(max_length=200)

    def __str__(self):
        return self.notes
