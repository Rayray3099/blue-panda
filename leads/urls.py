from django.urls import path
from .views import (LeadListView, LeadCreateView, LeadUpdateView, LeadDeleteView, LeadListNote, LeadDeleteNote, LeadListReview, LeadDeleteReview, LeadUploadView)

app_name = "leads"

urlpatterns = [
    path('', LeadListView.as_view(), name='lead-list'),
    path('<int:pk>/update/', LeadUpdateView.as_view(), name='lead-update'),
    path('<int:pk>/delete/', LeadDeleteView.as_view(), name='lead-delete'),
    path('<int:pk>/note/', LeadListNote.as_view(), name='lead-list-note'),
    path('note/<int:pk>/', LeadDeleteNote.as_view(), name='lead-delete-note'),
    path('<int:pk>/review/', LeadListReview.as_view(), name='lead-list-review'),
    path('review/<int:pk>/', LeadDeleteReview.as_view(), name='lead-delete-review'),
    path('create/', LeadCreateView.as_view(), name='lead-create'),
    path('upload/', LeadUploadView.as_view(), name='lead-upload'),
    ]
