from django.db import models
from django.utils import timezone
from django.db.models import Avg
from leads.models import User

class Product(models.Model):
    
    ACTIVE_CHOICES = (
        ('YES','YES'),
        ('NO', 'NO'),
    )

    product_code = models.CharField(max_length=64)
    brand_name = models.CharField(max_length=64)
    brand_family = models.CharField(max_length=64)
    internal_code = models.CharField(max_length=64)
    upc = models.CharField(max_length=64)
    part_number = models.CharField(max_length=64)
    product_title = models.CharField(max_length=64)
    product_description = models.CharField(max_length=128)
    sell_price = models.FloatField()
    cost_price = models.FloatField()
    inventory_count = models.IntegerField()
    product_material = models.CharField(max_length=64)
    product_color = models.CharField(max_length=64)
    product_length = models.FloatField(null=True, blank=True)
    product_width = models.FloatField(null=True, blank=True)
    product_height = models.FloatField(null=True, blank=True)
    product_volume = models.FloatField(null=True, blank=True)
    product_weight = models.FloatField(null=True, blank=True)
    product_image_one = models.CharField(max_length=512, blank=True, null=True)
    product_image_two = models.CharField(max_length=512, blank=True, null=True)
    product_image_three = models.CharField(max_length=512, blank=True, null=True)
    product_image_four = models.CharField(max_length=512, blank=True, null=True)
    product_image_five = models.CharField(max_length=512, blank=True, null=True)
    date_added = models.DateTimeField(default=timezone.now)
    date_modified = models.DateTimeField(default=timezone.now)
    multi_select = models.BooleanField(default=False)
    active = models.CharField(max_length=6, choices=ACTIVE_CHOICES, default='YES')

    @property
    def get_avg_rating(self):
        reviews = ProductReviews.objects.filter(product=self).aggregate(rating_avg=Avg('stars'))
        ratings = reviews['rating_avg']

        if ratings is not None:
            ratings = round(ratings, 2)
        else:
            ratings = 0
            
        return int(ratings)
    
    def __str__(self):
        return f"{self.product_code} {self.product_title}"

class ProductNotes(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date_added = models.DateTimeField(default=timezone.now)
    notes = models.CharField(max_length=200)

    def __str__(self):
        return self.notes

class ProductReviews(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date_added = models.DateTimeField(default=timezone.now)
    stars = models.IntegerField(default=5, blank=True, null=True)
    reviews = models.CharField(max_length=200)

    def __str__(self):
        return str(self.stars)
