from django.urls import path
from .views import SupplierListView, SupplierCreateView, SupplierUploadView, SupplierUpdateView, SupplierDeleteView, SupplierListNote, SupplierDeleteNote, SupplierListReview, SupplierDeleteReview

app_name = 'suppliers'

urlpatterns = [
    path('', SupplierListView.as_view(), name='supplier-list'),
    path('create/', SupplierCreateView.as_view(), name='supplier-create'),
    path('upload/', SupplierUploadView.as_view(), name='supplier-upload'),
    path('<int:pk>/update/', SupplierUpdateView.as_view(), name='supplier-update'),
    path('<int:pk>/delete/', SupplierDeleteView.as_view(), name='supplier-delete'),
    path('<int:pk>/note/', SupplierListNote.as_view(), name='supplier-list-note'),
    path('note/<int:pk>/', SupplierDeleteNote.as_view(), name='supplier-delete-note'),
    path('<int:pk>/review/', SupplierListReview.as_view(), name='supplier-list-review'),
    path('review/<int:pk>/', SupplierDeleteReview.as_view(), name='supplier-delete-review'),
    ]
