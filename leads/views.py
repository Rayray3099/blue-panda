import csv, io
import pandas as pd
import time
from django.contrib import messages
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.utils.datastructures import MultiValueDictKeyError
from django.views import generic
from .models import Lead, LeadNotes, LeadReviews, Agent, User
from .forms import LeadNoteForm, LeadReviewForm, LeadModelForm, CustomUserCreationForm

class SignupView(generic.CreateView):
    template_name = "registration/signup.html"
    form_class = CustomUserCreationForm

    def get_success_url(self):
        return reverse("login")

class LandingPageView(generic.TemplateView):
    template_name = "landing.html"

class LeadListView(LoginRequiredMixin, generic.ListView):
    template_name = "leads/lead_list.html"
    paginate_by = 50
    ordering = ['first_name']

    def get_paginate_by(self, queryset):
        return self.request.GET.get('paginate_by', self.paginate_by)

    def get_ordering(self):
        self.order = self.request.GET.get('order', 'asc')
        selected_ordering = self.request.GET.get('ordering', '-date_added')
        if self.order == "desc":
            selected_ordering = "-" + selected_ordering
        return selected_ordering

    def get_context_data(self, *args, **kwargs):
        context = super(LeadListView, self).get_context_data(*args, **kwargs)
        context['current_order'] = self.get_ordering()
        context['order'] = self.order
        context['active_list'] = Lead.objects.filter(active="YES")
        context['none_active_list'] = Lead.objects.filter(active="NO")
        return context

    def get_queryset(self, query=None, active_query=None):
        query = self.request.GET.get('q')
        self.active_filter = self.request.GET.get('active')
        ordering = self.get_ordering()

        if query:
            object_list = Lead.objects.filter(active=active_filter) & Lead.objects.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(address__icontains=query) |
                Q(zip_code__icontains=query) |
                Q(home_phone__icontains=query) |        
                Q(email__icontains=query)
                ).order_by(ordering)

        elif self.active_filter=="NO":
            object_list = Lead.objects.all().filter(active="NO").order_by(ordering)
            self.active_filter="NO"

        else:
            object_list = Lead.objects.all().filter(active="YES").order_by(ordering)
            self.active_filter="YES"
   
        return object_list

    def post(self, request, *args, **kwargs):
        if request.POST.get('export_csv'):
            self.object_list = self.get_queryset()
            
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment;filename=export_lead.csv'

            # opts = queryset.model._meta
            export_header_names = ['first_name', 'last_name', 'address', 'city', 'province', 'country', 'zip_code', 'home_phone', 'work_phone', 'email']

            writer = csv.writer(response)
            writer.writerow(export_header_names)

            for row in self.object_list:
                writer.writerow([row.first_name, row.last_name, row.address, row.city, row.province, row.country, row.zip_code, row.home_phone, row.work_phone, row.email])
            return response

        if request.POST.get('bulk_delete'):
            self.object_list = self.get_queryset()

            if 'delete_all' in request.POST:
                delete_list = self.object_list.values_list('id', flat=True)
            else:   
                delete_list = request.POST.getlist('multi_delete')

            for each_id in delete_list:
                Lead.objects.get(id=each_id).delete()

            return redirect("leads:lead-list")

        if request.POST.get('bulk_deactivate'):
            self.object_list = self.get_queryset()

            if 'delete_all' in request.POST:
                deactivate_list = self.object_list.values_list('id', flat=True)
            else:   
                deactivate_list = request.POST.getlist('multi_delete')

            for each_id in deactivate_list:
                Lead.objects.filter(id=each_id).update(active='NO')

            return redirect("leads:lead-list")

class LeadUploadView(LoginRequiredMixin, generic.ListView):
    template_name = "leads/lead_upload.html"
    queryset = Lead.objects.all()
    
    def post(self, request, *args, **kwargs):
        
        header_original = ['first_name', 'last_name', 'address', 'city', 'province', 'country', 'zip_code', 'home_phone', 'work_phone', 'email']
        header_count = len(header_original)


        if request.POST.get('import_csv'):

            csv_file = request.FILES['file']

            # Check if file ends with csv
            if csv_file.name.endswith('.csv'):
                df_model_test = pd.DataFrame(list(Lead.objects.all().values('id')))
                print(df_model_test)

            else:
                messages.info(request, 'File format is not .csv')
                return render(request, "leads/lead_upload.html", {}) 

            # Check for keys from existing data            
            if not df_model_test.empty:
                df_from_model_id = df_model_test
                df_from_model_id_filtered = df_from_model_id['id'].values.tolist()
                df_from_model = pd.DataFrame(list(Lead.objects.all().values('first_name', 'last_name', 'home_phone')))
                df_from_model.applymap(lambda x: x.strip() if isinstance(x, str) else x)                       
                df_from_model_key = list(df_from_model['first_name'] + df_from_model['last_name'] + df_from_model['home_phone'].str.replace("-","").str.replace("(","").str.replace(")",""))
                           
            else:
                df_from_model_key = []

            df = pd.read_csv(csv_file)
            df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

            # Check if columns contain key info
            if 'first_name' in df.columns and 'last_name' in df.columns and 'home_phone' in df.columns:
                lead_keys = True
            else:
                messages.info(request, 'Headers missing, key columns (first_name, last_name, home_phone) are missing.')
                return render(request, "leads/lead_upload.html", {}) 
                lead_keys = False

            df_from_csv = df[['first_name', 'last_name', 'home_phone']]
            df_from_csv_key = list(df_from_csv['first_name'] + df_from_csv['last_name'] + df_from_csv['home_phone'].str.replace("-","").str.replace("(","").str.replace(")",""))

            try:            
                match_positions = [i for i, item in enumerate(df_from_csv_key) if item in df_from_model_key]
            except TypeError:
                match_positions = 0
                
            try:
                diff_positions = [i for i, item in enumerate(df_from_csv_key) if item not in df_from_model_key]
            except TypeError:
                diff_positions = 0
            
            pk_numbers = []
            if len(match_positions) != 0:
                match_id = [i for i, item in enumerate(df_from_model_key) if item in df_from_csv_key]
                df_update = df.iloc[match_positions,:]
                df_update_all = df_update[['first_name', 'last_name']]

                for each in match_id:
                    pk_numbers.append(df_from_model_id_filtered[each])

                if 'address' in df_update.columns:
                    address = df_update['address'].tolist()                    
                    for x, y in zip(pk_numbers, address):
                        Lead.objects.filter(id = x).update(address=y)

                if 'city' in df_update.columns:
                    city = df_update['city']
                    for x, y in zip(pk_numbers, city):
                        Lead.objects.filter(id = x).update(city=y)

                if 'province' in df_update.columns:
                    province = df_update['province']
                    for x, y in zip(pk_numbers, province):
                        Lead.objects.filter(id = x).update(province=y)

                if 'country' in df_update.columns:
                    country = df_update['country']
                    for x, y in zip(pk_numbers, country):
                        Lead.objects.filter(id = x).update(country=y)

                if 'zip_code' in df_update.columns:
                    zip_code = df_update['zip_code']
                    for x, y in zip(pk_numbers, zip_code):
                        Lead.objects.filter(id = x).update(zip_code=y)

                if 'work_phone' in df_update.columns:
                    work_phone = df_update['work_phone']
                    for x, y in zip(pk_numbers, work_phone):
                        Lead.objects.filter(id = x).update(work_phone=y)

                if 'email' in df_update.columns:
                    email = df_update['email']
                    for x, y in zip(pk_numbers, email):
                        Lead.objects.filter(id = x).update(email=y)

                if 'active' in df_update.columns:
                    active = df_update['active']
                    for x, y in zip(pk_numbers, active):
                        Lead.objects.filter(id = x).update(active=y)

                # This section adds new records after update the exisiting records
                if len(diff_positions) != 0:
                    df_create = df.iloc[diff_positions,:]            
                    row_iter_create = df_create.iterrows()

                    try:
                        objs = [
                            Lead(
                                first_name = row['first_name'],
                                last_name = row['last_name'],
                                address  = row['address'],
                                city  = row['city'],
                                province = row['province'],
                                country = row['country'],
                                zip_code  = row['zip_code'],
                                home_phone  = row['home_phone'],
                                work_phone = row['work_phone'],
                                email  = row['email'],
                            )
                            for index, row in row_iter_create
                        ]

                        Lead.objects.bulk_create(objs)
                        messages.info(request, 'Woohoo both update and import successful! ' + str(len(diff_positions)) + ' records are added')
                        return render(request, "leads/lead_upload.html", {})
                    
                    except Exception as e:
                        messages.info(request, 'For new upload please make sure all headers are in csv file and follow the template. Use (first_name, last_name, address...) make sure spelling and _ are correct.')
                        return render(request, "leads/lead_upload.html", {})
  
                messages.info(request, 'Hooray update successful! ' + str(len(match_positions)) + ' records are updated')
                return render(request, "leads/lead_upload.html", {})

            elif len(match_positions) == 0:
                df_create = df.iloc[diff_positions,:]            
                row_iter_create = df_create.iterrows()
                
                objs = [
                    Lead(
                        first_name = row['first_name'],
                        last_name = row['last_name'],
                        address  = row['address'],
                        city  = row['city'],
                        province = row['province'],
                        country = row['country'],
                        zip_code  = row['zip_code'],
                        home_phone  = row['home_phone'],
                        work_phone = row['work_phone'],
                        email  = row['email'],
                    )
                    for index, row in row_iter_create
                ]

                Lead.objects.bulk_create(objs)
                messages.info(request, 'First import successful! ' + str(len(diff_positions)) + ' records are added')
                return render(request, "leads/lead_upload.html", {})

            else:
                messages.info(request, 'No update or import was found!')
                return render(request, "leads/lead_upload.html", {})

class LeadCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = "leads/lead_create.html"
    form_class = LeadModelForm

    def get_success_url(self):
        return reverse("leads:lead-list")

    def form_valid(self, form):
        return super(LeadCreateView, self).form_valid(form)

class LeadUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Lead
    template_name = "leads/lead_update.html"
    form_class = LeadModelForm
    
    def get_success_url(self):
        return reverse("leads:lead-list")

class LeadDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Lead
    template_name = "leads/lead_delete.html"

    def get_success_url(self):
        return reverse("leads:lead-list")

class LeadListNote(LoginRequiredMixin, generic.CreateView):
    template_name = "leads/lead_list_note.html"
    form_class = LeadNoteForm

    def get_context_data(self, **kwargs):        
        context = super(LeadListNote, self).get_context_data(**kwargs)
        context['object_list'] = int(Lead.objects.filter(id=self.kwargs['pk']).values_list('id',flat=True)[0])      
        context['note_list'] = LeadNotes.objects.filter(lead_id=self.kwargs['pk'])
        
        try:
            context['note_update_list'] = list(LeadNotes.objects.filter(author_id=self.request.user.id, lead_id=self.kwargs['pk']).values_list('id',flat=True))
        except IndexError:
            pass

        return context

    def form_valid(self, form):
        form.instance.author_id = self.request.user.id
        form.instance.lead_id = self.kwargs['pk']
        return super(LeadListNote, self).form_valid(form)

    def get_success_url(self):
        return self.request.path

class LeadDeleteNote(LoginRequiredMixin, generic.DeleteView):
    model = LeadNotes
    template_name = "leads/lead_delete_note.html"

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author_id != self.request.user.id:
            raise PermissionDenied("User can't delete this question.")
        return super(LeadDeleteNote, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("leads:lead-list")

class LeadListReview(LoginRequiredMixin, generic.CreateView):
    template_name = "leads/lead_list_review.html"
    form_class = LeadReviewForm
    
    def get_context_data(self, **kwargs):
        context = super(LeadListReview, self).get_context_data(**kwargs)
        context['object_list'] = int(Lead.objects.filter(id=self.kwargs['pk']).values_list('id',flat=True)[0])
        context['review_list'] = LeadReviews.objects.filter(lead_id=self.kwargs['pk'])
        
        try:
            context['review_update_list'] = list(LeadReviews.objects.filter(author_id=self.request.user.id, lead_id=self.kwargs['pk']).values_list('id',flat=True))
        except IndexError:
            pass
        
        return context

    def form_valid(self, form):
        form.instance.author_id = self.request.user.id
        form.instance.lead_id = self.kwargs['pk']
        return super(LeadListReview, self).form_valid(form)

    def get_success_url(self):
        return self.request.path

class LeadDeleteReview(LoginRequiredMixin, generic.DeleteView):
    model = LeadReviews
    template_name = "leads/lead_delete_review.html"

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author_id != self.request.user.id:
            raise PermissionDenied("User can't delete this question.")
        return super(LeadDeleteReview, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("leads:lead-list")
