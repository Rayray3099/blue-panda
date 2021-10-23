from django.conf.urls import url
from django.urls import path
from . import views

app_name = 'cal'

urlpatterns = [
    path('', views.CalendarView.as_view(), name='calendar-view'),
    path('event/new/', views.event, name='event_new'),
    path('event/edit/<event_id>/', views.event, name='event_edit'),
]
