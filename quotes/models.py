from django.db import models
from django.utils import timezone
from django.db.models import Avg
from leads.models import User, Lead
from products.models import Product

import time
import datetime

def create_id():
    now = datetime.datetime.now()
    return str(now.year)+str(now.month)+str(now.day)+str(now.hour)+str(now.minute)+str(now.second)+str("-")+str(now.microsecond)

def current_milli_time():
    return round(time.time() * 1000)

class Quote(models.Model):
    
    ACTIVE_CHOICES = (
        ('YES','YES'),
        ('NO', 'NO'),
    )

    quote_id = models.CharField(max_length=64, default=create_id)

    customer = models.ForeignKey(Lead, on_delete=models.PROTECT)
    
    date_added = models.DateTimeField(default=timezone.now)
    date_modified = models.DateTimeField(default=timezone.now)
    multi_select = models.BooleanField(default=False)
    active = models.CharField(max_length=6, choices=ACTIVE_CHOICES, default='YES')
    
    def __str__(self):
        return f"{self.customer}"


class QuoteProducts(models.Model):

    STATUS_CHOICES = (
        ('UNPAID','UNPAID'),
        ('PAID', 'PAID'),
    )
    
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE)
    product_select = models.ForeignKey(Product, on_delete=models.PROTECT)
    product_quantity = models.IntegerField(default=1)
    product_price = models.FloatField(default=0)
    date_added = models.DateTimeField(blank=True, null=True, default=timezone.now)

    product_sub_total = models.FloatField(default=0)

    quote_status = models.CharField(max_length=64, choices=STATUS_CHOICES, default='UNPAID')

    def __str__(self):
        return f"{self.product_select}"


class QuoteNotes(models.Model):
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date_added = models.DateTimeField(default=timezone.now)
    notes = models.CharField(max_length=200)

    def __str__(self):
        return self.notes

