from django.urls import path
from .views import QuoteListView, QuoteCreateView, QuoteUploadView, QuoteUpdateView, QuoteDeleteView, QuoteListNote, QuoteDeleteNote, QuoteListReview, QuoteDeleteReview

app_name = 'quotes'

urlpatterns = [
    path('', QuoteListView.as_view(), name='quote-list'),
    path('create/', QuoteCreateView.as_view(), name='quote-create'),
    path('upload/', QuoteUploadView.as_view(), name='quote-upload'),
    path('<int:pk>/update/', QuoteUpdateView.as_view(), name='quote-update'),
    path('<int:pk>/delete/', QuoteDeleteView.as_view(), name='quote-delete'),
    path('<int:pk>/note/', QuoteListNote.as_view(), name='quote-list-note'),
    path('note/<int:pk>/', QuoteDeleteNote.as_view(), name='quote-delete-note'),
    path('<int:pk>/review/', QuoteListReview.as_view(), name='quote-list-review'),
    path('review/<int:pk>/', QuoteDeleteReview.as_view(), name='quote-delete-review'),
    ]
