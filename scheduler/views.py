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

from leads.models import Lead, User
from products.models import Product
from quotes.models import QuoteProducts

from .models import Schedule, ScheduleItems, ScheduleNotes
from .forms import ScheduleModelForm, ScheduleItemForm, ScheduleNoteForm


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
        context['active_list'] = Schedule.objects.all().filter(user=self.request.user)
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
                writer.writerow([row.schedule_id, row.user_id, row.schedule_day, row.alarm_day, row.schedule_notes])
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
    model = Schedule
    template_name = "scheduler/schedule_create.html"
    form_class = ScheduleModelForm

    def get_success_url(self):
        return reverse("scheduler:schedule-list")

    def form_valid(self, form):
        return super(ScheduleCreateView, self).form_valid(form)

class ScheduleUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Schedule
    template_name = "scheduler/schedule_update.html"
    form_class = ScheduleItemForm

    def get_context_data(self, **kwargs):
        context = super(ScheduleUpdateView, self).get_context_data(**kwargs)
        schedule = Schedule.objects.get(pk=self.kwargs.get('pk'))
        
        if self.request.POST:
            context['schedule_select'] = ScheduleItemForm(self.request.POST, instance=schedule)
            context['schedule_list'] = ScheduleItems.objects.filter(schedule_id=self.kwargs['pk'])

        else:
            context['schedule_select'] = ScheduleItemForm(instance=schedule)
            context['schedule_list'] = ScheduleItems.objects.filter(schedule_id=self.kwargs['pk'])
           
        return context

    def post(self, request, *args, **kwargs):
        schedule = Schedule.objects.get(pk=self.kwargs.get('pk'))

        if request.method=='POST' and 'add_cart' in request.POST:
            
            current_time = request.POST['schedule_time']
            current_item = request.POST['schedule_item']
            
            new_entry = ScheduleItems(schedule_id=self.kwargs.get('pk'), schedule_time=current_time, schedule_item=current_item)
            new_entry.save()

            return HttpResponseRedirect(self.request.path_info)

        if request.method=='POST' and 'multi_delete' in request.POST:
            delete_list = request.POST.getlist('multi_delete')

            for each_id in delete_list:
                ScheduleItems.objects.get(id=each_id).delete()

            return HttpResponseRedirect(self.request.path_info)

        return redirect("scheduler:schedule-list")
            
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





class ScheduleUploadView(LoginRequiredMixin, generic.ListView):
    template_name = "scheduler/schedule_upload.html"
    queryset = Schedule.objects.all()
    
    def post(self, request, *args, **kwargs):
        
        header_original = ['schedule_id', 'user', 'date_added', 'schedule_day', 'alarm_day', 'schedule_notes']
        header_count = len(header_original)

        if request.POST.get('import_csv'):

            csv_file = request.FILES['file']

            if csv_file.name.endswith('.csv'):
                df_model_test = pd.DataFrame(list(Schedule.objects.all().values('id')))

            else:
                messages.info(request, 'File format is not .csv')
                return render(request, "scheduler/schedule_upload.html", {}) 

            # Check for keys from existing data            
            if not df_model_test.empty:
                df_from_model_id = df_model_test
                df_from_model_id_filtered = df_from_model_id['id'].values.tolist()

                print("This is df_from_model_id_filtered")
                print(df_from_model_id_filtered)
                
                df_from_model = pd.DataFrame(list(Schedule.objects.all().values('user', 'schedule_day', 'alarm_day')))
                df_from_model.applymap(lambda x: x.strip() if isinstance(x, str) else x)
                
                df_from_model_key_user = list(df_from_model['user'])
                df_from_model_key_sday = list(df_from_model['schedule_day'])
                df_from_model_key_aday = list(df_from_model['alarm_day'])

                df_from_model_key = []

                for x,y,z in zip(df_from_model_key_user, df_from_model_key_sday, df_from_model_key_aday):
                    each_key = str(x) + str(y) + str(z)
                    df_from_model_key.append(each_key)
                    
                print(df_from_model_key)
                           
            else:
                df_from_model_key = []


            print("model key ")
            print(df_from_model_key)


            df = pd.read_csv(csv_file)
            df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

            # Check if columns contain key info
            if 'user' in df.columns and 'schedule_day' in df.columns and 'alarm_day' in df.columns:
                lead_keys = True
            else:
                messages.info(request, 'Headers missing, key columns (user, schedule_day, alarm_day) are missing.')
                return render(request, "scheduler/schedule_upload.html", {}) 
                lead_keys = False

            df_from_csv = df[['user', 'schedule_day', 'alarm_day']]

            df_from_csv_key_user = list(df_from_csv['user'])
            df_from_csv_key_sday = list(df_from_csv['schedule_day'])
            df_from_csv_key_aday = list(df_from_csv['alarm_day'])

            df_from_csv_key = []

            for x,y,z in zip(df_from_csv_key_user, df_from_csv_key_sday, df_from_csv_key_aday):
                each_key = str(x) + str(y) + str(z)
                df_from_csv_key.append(each_key)

            print("df csv key ")
            print(df_from_csv_key)

            try:            
                match_positions = [i for i, item in enumerate(df_from_csv_key) if item in df_from_model_key]
            except TypeError:
                match_positions = 0
                
            try:
                diff_positions = [i for i, item in enumerate(df_from_csv_key) if item not in df_from_model_key]
            except TypeError:
                diff_positions = 0


            print("match")
            print(match_positions)

            print("different")
            print(diff_positions)

            
            pk_numbers = []
            if len(match_positions) != 0:
                match_id = [i for i, item in enumerate(df_from_model_key) if item in df_from_csv_key]
                df_update = df.iloc[match_positions,:]
                df_update_all = df_update[['schedule_day', 'alarm_day']]

                for each in match_id:
                    pk_numbers.append(df_from_model_id_filtered[each])

                if 'schedule_day' in df_update.columns:
                    schedule_day = df_update['schedule_day'].tolist()                    
                    for x, y in zip(pk_numbers, schedule_day):
                        Schedule.objects.filter(id = x).update(schedule_day=y)

                if 'alarm_day' in df_update.columns:
                    alarm_day = df_update['alarm_day']
                    for x, y in zip(pk_numbers, alarm_day):
                        Schedule.objects.filter(id = x).update(alarm_day=y)

                # This section adds new records after update the exisiting records
                if len(diff_positions) != 0:
                    df_create = df.iloc[diff_positions,:]            
                    row_iter_create = df_create.iterrows()

                    try:
                        objs = [
                            Schedule(
                                schedule_day = row['schedule_day'],
                                alarm_day = row['alarm_day'],
                            )
                            for index, row in row_iter_create
                        ]

                        Schedule.objects.bulk_create(objs)
                        messages.info(request, 'Woohoo both update and import successful! ' + str(len(diff_positions)) + ' records are added')
                        return render(request, "scheduler/schedule_upload.html", {})
                    
                    except Exception as e:
                        messages.info(request, 'For new upload please make sure all headers are in csv file and follow the template. Use (first_name, last_name, address...) make sure spelling and _ are correct.')
                        return render(request, "scheduler/schedule_upload.html", {})
  
                messages.info(request, 'Hooray update successful! ' + str(len(match_positions)) + ' records are updated')
                return render(request, "scheduler/schedule_upload.html", {})

            if len(diff_positions) != 0:
                df_create = df.iloc[diff_positions,:]            
                row_iter_create = df_create.iterrows()

                try:
                    objs = [
                        Schedule(
                                schedule_day = row['schedule_day'],
                                alarm_day = row['alarm_day'],
                        )
                        for index, row in row_iter_create
                    ]

                    Schedule.objects.bulk_create(objs)
                    messages.info(request, 'Yay import successful! ' + str(len(diff_positions)) + ' records are added')
                    return render(request, "scheduler/schedule_upload.html", {})
                
                except Exception as e:
                    messages.info(request, 'For new upload please make sure all headers are in csv file and follow the template. Use (first_name, last_name, address...) make sure spelling and _ are correct.')
                    return render(request, "scheduler/schedule_upload.html", {})
            else:
                messages.info(request, 'No update or import was found!')
                return render(request, "scheduler/schedule_upload.html", {})
