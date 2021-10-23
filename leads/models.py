from django.db import models
from django.utils import timezone
from django.db.models import Avg
from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_organisor = models.BooleanField(default=True)
    is_agent = models.BooleanField(default=False)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

class Lead(models.Model):

    ACTIVE_CHOICES = (
        ('YES','YES'),
        ('NO', 'NO'),
    )
    
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
    agent = models.CharField(max_length=20)
    #agent = models.ForeignKey(Agent, default=1, on_delete=models.SET_DEFAULT)
    date_added = models.DateTimeField(default=timezone.now)
    date_modified = models.DateTimeField(default=timezone.now)
    multi_select = models.BooleanField(default=False)
    active = models.CharField(max_length=6, choices=ACTIVE_CHOICES, default='YES')

    @property
    def get_avg_rating(self):
        reviews = LeadReviews.objects.filter(lead=self).aggregate(rating_avg=Avg('stars'))
        ratings = reviews['rating_avg']

        if ratings is not None:
            ratings = round(ratings, 2)
        else:
            ratings = 0
            
        return int(ratings)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class LeadNotes(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date_added = models.DateTimeField(default=timezone.now)
    notes = models.CharField(max_length=200)

    def __str__(self):
        return self.notes

class LeadReviews(models.Model):
    lead = models.ForeignKey(Lead, related_name='reviews', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date_added = models.DateTimeField(default=timezone.now)
    stars = models.IntegerField(default=5, blank=True, null=True)
    reviews = models.CharField(max_length=200)

    def __str__(self):
        return str(self.stars)

class Agent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organisation = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

def post_user_created_signal(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(post_user_created_signal, sender=User)
