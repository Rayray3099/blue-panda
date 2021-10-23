from django.urls import path
from .views import ProductListView, ProductCreateView, ProductUploadView, ProductUpdateView, ProductDeleteView, ProductListNote, ProductDeleteNote, ProductListReview, ProductDeleteReview

app_name = 'products'

urlpatterns = [
    path('', ProductListView.as_view(), name='product-list'),
    path('create/', ProductCreateView.as_view(), name='product-create'),
    path('upload/', ProductUploadView.as_view(), name='product-upload'),
    path('<int:pk>/update/', ProductUpdateView.as_view(), name='product-update'),
    path('<int:pk>/delete/', ProductDeleteView.as_view(), name='product-delete'),
    path('<int:pk>/note/', ProductListNote.as_view(), name='product-list-note'),
    path('note/<int:pk>/', ProductDeleteNote.as_view(), name='product-delete-note'),
    path('<int:pk>/review/', ProductListReview.as_view(), name='product-list-review'),
    path('review/<int:pk>/', ProductDeleteReview.as_view(), name='product-delete-review'),
    ]
