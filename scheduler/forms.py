from django import forms
from .models import Schedule, ScheduleItems, ScheduleNotes

import datetime
import requests


class DateInput(forms.DateInput):
    input_type = 'date'

class TimeInput(forms.TimeInput):
    input_type = 'time'

class ScheduleModelForm(forms.ModelForm):

    schedule_day = forms.DateField(widget=DateInput)
    alarm_day = forms.DateField(widget=DateInput)

    schedule_notes = forms.CharField(widget=forms.Textarea(attrs={'cols':50, 'rows': 3, 'style': 'width: 100%',}))
    
    class Meta:
        model = Schedule
        
        fields = (
            'schedule_day',
            'alarm_day',
            'schedule_notes',
            )
            
    def __init__(self, *args, **kwargs):
        super(ScheduleModelForm, self).__init__(*args, **kwargs)


class ScheduleItemForm(forms.ModelForm):

    schedule_time = forms.DateField(widget=TimeInput)

    class Meta:
        model = ScheduleItems
        fields = (
            'schedule_time',
            'schedule_item',
            )

    def __init__(self, *args, **kwargs):
        super(ScheduleItemForm, self).__init__(*args, **kwargs)


class ScheduleNoteForm(forms.ModelForm):

    notes = forms.CharField(widget=forms.Textarea(attrs={'cols':100, 'rows': 3, 'style': 'width: 100%',}))

    class Meta:
        model = ScheduleNotes
        fields = (
            'notes',
            )
