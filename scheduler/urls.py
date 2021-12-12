from django.urls import path
from .views import ScheduleListView, ScheduleDetailView, ScheduleListNote, ScheduleDeleteNote, ScheduleCreateView, ScheduleUpdateView, ScheduleDeleteView

app_name = 'scheduler'

urlpatterns = [
    path('', ScheduleListView.as_view(), name='schedule-list'),
    path('create/', ScheduleCreateView.as_view(), name='schedule-create'),
    path('<int:pk>/update/', ScheduleUpdateView.as_view(), name='schedule-update'),
    path('<int:pk>/delete/', ScheduleDeleteView.as_view(), name='schedule-delete'),
    path('<int:pk>/detail/', ScheduleDetailView.as_view(), name='schedule-detail'),
    path('<int:pk>/note/', ScheduleListNote.as_view(), name='schedule-list-note'),
    path('note/<int:pk>/', ScheduleDeleteNote.as_view(), name='schedule-delete-note'),
    ]
