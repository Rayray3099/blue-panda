from django.db import models
from django.utils import timezone
from django.db.models import Avg
from leads.models import User

class Supplier(models.Model):
    
    ACTIVE_CHOICES = (
        ('YES','YES'),
        ('NO', 'NO'),
    )

    business_name = models.CharField(max_length=128)
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    address = models.CharField(max_length=128)
    city = models.CharField(max_length=64)
    province = models.CharField(max_length=64)
    country = models.CharField(max_length=64)
    zip_code = models.CharField(max_length=20)
    home_phone = models.CharField(max_length=20)
    work_phone = models.CharField(max_length=20)
    email = models.EmailField()
    
    date_added = models.DateTimeField(default=timezone.now)
    date_modified = models.DateTimeField(default=timezone.now)
    multi_select = models.BooleanField(default=False)
    active = models.CharField(max_length=6, choices=ACTIVE_CHOICES, default='YES')

    @property
    def get_avg_rating(self):
        reviews = SupplierReviews.objects.filter(supplier=self).aggregate(rating_avg=Avg('stars'))
        ratings = reviews['rating_avg']

        if ratings is not None:
            ratings = round(ratings, 2)
        else:
            ratings = 0
            
        return int(ratings)
    
    def __str__(self):
        return f"{self.business_name}"

class SupplierNotes(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date_added = models.DateTimeField(default=timezone.now)
    notes = models.CharField(max_length=200)

    def __str__(self):
        return self.notes

class SupplierReviews(models.Model):
    supplier = models.ForeignKey(Supplier, related_name='reviews', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date_added = models.DateTimeField(default=timezone.now)
    stars = models.IntegerField(default=5, blank=True, null=True)
    reviews = models.CharField(max_length=200)

    def __str__(self):
        return str(self.stars)
