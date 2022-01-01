from django.urls import path
from .views import Reports

app_name = 'reports'

urlpatterns = [
    path('', Reports.as_view(), name='reports'),
    ]
