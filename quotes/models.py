from django.db import models
from django.utils import timezone
from django.db.models import Avg
from leads.models import User, Lead
from products.models import Product

class Quote(models.Model):
    ACTIVE_CHOICES = (
        ('YES','YES'),
        ('NO', 'NO'),
    )

    STATUS_CHOICES = (
        ('UNPAID','UNPAID'),
        ('PAID', 'PAID'),
    )

    quote_id = models.CharField(max_length=64)

    customer = models.ForeignKey(Lead, on_delete=models.PROTECT)
    products = models.ForeignKey(Product, on_delete=models.PROTECT)
    
    date_added = models.DateTimeField(default=timezone.now)
    date_modified = models.DateTimeField(default=timezone.now)
    multi_select = models.BooleanField(default=False)
    active = models.CharField(max_length=6, choices=ACTIVE_CHOICES, default='YES')
    status = models.CharField(max_length=64, choices=STATUS_CHOICES, default='UNPAID')
    
    def __str__(self):
        return f"{self.customer}"

class QuoteNotes(models.Model):
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date_added = models.DateTimeField(default=timezone.now)
    notes = models.CharField(max_length=200)

    def __str__(self):
        return self.notes

class QuoteReviews(models.Model):
    quote = models.ForeignKey(Quote, related_name='reviews', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date_added = models.DateTimeField(default=timezone.now)
    stars = models.IntegerField(default=5, blank=True, null=True)
    reviews = models.CharField(max_length=200)

    def __str__(self):
        return str(self.stars)

