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

class Schedule(models.Model):
    
    ACTIVE_CHOICES = (
        ('YES','YES'),
        ('NO', 'NO'),
    )

    schedule_id = models.CharField(max_length=64, default=create_id)
    user = models.ForeignKey(User, on_delete=models.PROTECT, default=1)
    date_added = models.DateTimeField(blank=True, null=True, default=timezone.now)

    schedule_day = models.CharField(max_length=64)
    alarm_day = models.CharField(max_length=64)

    schedule_notes = models.CharField(max_length=200)
    
    multi_select = models.BooleanField(default=False)
    active = models.CharField(max_length=6, choices=ACTIVE_CHOICES, default='YES')
    
    def __str__(self):
        return f"{self.user}"

class ScheduleNotes(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date_added = models.DateTimeField(blank=True, null=True, default=timezone.now)
    notes = models.CharField(max_length=200)

    def __str__(self):
        return self.notes
