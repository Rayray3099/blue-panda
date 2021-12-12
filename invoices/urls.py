from django.urls import path
from .views import InvoiceListView, InvoiceDetailView, InvoiceListNote, InvoiceDeleteNote

app_name = 'invoices'

urlpatterns = [
    path('', InvoiceListView.as_view(), name='invoice-list'),
    path('<int:pk>/detail/', InvoiceDetailView.as_view(), name='invoice-detail'),
    path('<int:pk>/note/', InvoiceListNote.as_view(), name='invoice-list-note'),
    path('note/<int:pk>/', InvoiceDeleteNote.as_view(), name='invoice-delete-note'),
    ]
