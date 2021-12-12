import csv, io
import pandas as pd
import json
import datetime

from django.contrib import messages
from django.views import generic

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from django.http import HttpResponseRedirect

from leads.models import Lead
from products.models import Product
from quotes.models import QuoteProducts

from .models import Schedule, ScheduleNotes

from .forms import ScheduleModelForm, ScheduleNoteForm


class ScheduleListView(LoginRequiredMixin, generic.ListView):
    template_name = "scheduler/schedule_list.html"
    paginate_by = 50
    ordering = ['id']

    def get_paginate_by(self, queryset):
        return self.request.GET.get('paginate_by', self.paginate_by)

    def get_ordering(self):
        self.order = self.request.GET.get('order', 'asc')
        selected_ordering = self.request.GET.get('ordering', '-date_added')
        if self.order == "desc":
            selected_ordering = "-" + selected_ordering
        return selected_ordering

    def get_context_data(self, *args, **kwargs):
        context = super(ScheduleListView, self).get_context_data(*args, **kwargs)
        context['current_order'] = self.get_ordering()
        context['order'] = self.order
        context['active_list'] = Schedule.objects.all()
        return context

    def get_queryset(self, query=None):
        query = self.request.GET.get('q')
        active_filter = self.request.GET.get('active')
        ordering = self.get_ordering()
        
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        if query:                
            object_list = Schedule.objects.filter(
                Q(schedule_notes__icontains=query) |
                Q(schedule_day__icontains=query) |
                Q(alarm_day__icontains=query))

        elif start_date and end_date:
            object_list = Schedule.objects.filter(
                Q(schedule_notes__icontains=query) |
                Q(schedule_day__icontains=query) |
                Q(alarm_day__icontains=query)).filter(date_added__range=(start_date, end_date))
        
        elif active_filter=="NO":
            object_list = Schedule.objects.all()
            
        else:
            object_list = Schedule.objects.all()
   
        return object_list


    def post(self, request, *args, **kwargs):
        if request.POST.get('export_csv'):
            self.object_list = self.get_queryset()
            
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment;filename=export_schedule.csv'

            export_header_names = ['schedule_id', 'user', 'schedule_day', 'alarm_day', 'schedule_notes']

            writer = csv.writer(response)
            writer.writerow(export_header_names)

            for row in self.object_list:
                writer.writerow([row.schedule_id, row.user, row.schedule_day, row.alarm_day, row.schedule_notes])
            return response

        if request.POST.get('bulk_delete'):
            self.object_list = self.get_queryset()

            if 'delete_all' in request.POST:
                delete_list = self.object_list.values_list('id', flat=True)
            else:   
                delete_list = request.POST.getlist('multi_delete')

            for each_id in delete_list:
                Schedule.objects.get(id=each_id).delete()

            return redirect("scheduler:schedule-list")

        if request.POST.get('bulk_deactivate'):
            self.object_list = self.get_queryset()

            if 'delete_all' in request.POST:
                deactivate_list = self.object_list.values_list('id', flat=True)
            else:   
                deactivate_list = request.POST.getlist('multi_delete')

            for each_id in deactivate_list:
                Schedule.objects.filter(id=each_id).update(active='NO')

            return redirect("scheduler:schedule-list")

class ScheduleCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = "scheduler/schedule_create.html"
    form_class = ScheduleModelForm

    def get_success_url(self):
        return reverse("scheduler:schedule-list")

    def form_valid(self, form):
        return super(ScheduleCreateView, self).form_valid(form)

class ScheduleUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Schedule
    template_name = "scheduler/schedule_update.html"
    form_class = ScheduleModelForm
            
    def get_success_url(self):
        return reverse("scheduler:schedule-list")

class ScheduleDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Schedule
    template_name = "scheduler/schedule_delete.html"

    def get_success_url(self):
        return reverse("scheduler:schedule-list")




class ScheduleDetailView(LoginRequiredMixin, generic.DetailView):    
    model = Schedule
    template_name = "scheduler/schedule_detail.html"

    def get_context_data(self, *args, **kwargs):
        context = super(ScheduleDetailView, self).get_context_data(**kwargs)
        #quote_key = Schedule.objects.get(pk=self.kwargs.get('pk'))
        
        context['schedule'] = Schedule.objects.get(pk=self.kwargs.get('pk'))
        #context['product_list'] = QuoteProducts.objects.filter(quote_id=quote_key.quote_id)
        return context

class ScheduleListNote(LoginRequiredMixin, generic.CreateView):
    template_name = "scheduler/schedule_list_note.html"
    form_class = ScheduleNoteForm

    def get_context_data(self, **kwargs):        
        context = super(ScheduleListNote, self).get_context_data(**kwargs)
        context['object_list'] = int(Schedule.objects.filter(id=self.kwargs['pk']).values_list('id',flat=True)[0])      
        context['note_list'] = ScheduleNotes.objects.filter(schedule_id=self.kwargs['pk'])
        
        try:
            context['note_update_list'] = list(ScheduleNotes.objects.filter(author_id=self.request.user.id, schedule_id=self.kwargs['pk']).values_list('id',flat=True))
        except IndexError:
            pass

        return context

    def form_valid(self, form):
        form.instance.author_id = self.request.user.id
        form.instance.schedule_id = self.kwargs['pk']
        return super(ScheduleListNote, self).form_valid(form)

    def get_success_url(self):
        return self.request.path

class ScheduleDeleteNote(LoginRequiredMixin, generic.DeleteView):
    model = ScheduleNotes
    template_name = "scheduler/schedule_delete_note.html"

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author_id != self.request.user.id:
            raise PermissionDenied("User can't delete this question.")
        return super(ScheduleDeleteNote, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("scheduler:schedule-list")
