from django.urls import path
from .views import InvoiceListView, InvoiceDetailView

app_name = 'invoices'

urlpatterns = [
    path('', InvoiceListView.as_view(), name='invoice-list'),
    path('<int:pk>/detail/', InvoiceDetailView.as_view(), name='invoice-detail'),
    ]
