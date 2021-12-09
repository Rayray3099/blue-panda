import csv, io
import pandas as pd
import json
import datetime

from django.contrib import messages
from django.views import generic
from django.views.generic import FormView
from django.views.generic.detail import SingleObjectMixin

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from django.http import HttpResponseRedirect

from leads.models import Lead
from products.models import Product
from invoices.models import Invoice

from .models import Quote, QuoteNotes, QuoteProducts
from .forms import QuoteModelForm, QuoteNoteForm, QuoteProductForm


class QuoteListView(LoginRequiredMixin, generic.ListView):
    template_name = "quotes/quote_list.html"
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
        context = super(QuoteListView, self).get_context_data(*args, **kwargs)
        context['current_order'] = self.get_ordering()
        context['order'] = self.order
        context['active_list'] = Quote.objects.filter(active="YES")
        context['none_active_list'] = Quote.objects.filter(active="NO")
        return context

    def get_queryset(self, query=None):
        query = self.request.GET.get('q')
        active_filter = self.request.GET.get('active')
        ordering = self.get_ordering()

        if query:
            object_list = Quote.objects.filter(active=active_filter) & Quote.objects.filter(
                Q(customer__icontains=query) |
                Q(products__icontains=query) |
                Q(quote_id__icontains=query))
            
        elif active_filter=="NO":
            object_list = Quote.objects.all().filter(active="NO")#.order_by(ordering)
            
        else:
            object_list = Quote.objects.all().filter(active="YES")#.order_by(ordering)
   
        return object_list

    def post(self, request, *args, **kwargs):
        if request.POST.get('export_csv'):
            self.object_list = self.get_queryset()
            
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment;filename=export_quote.csv'

            export_header_names = ['first_name', 'last_name', 'address', 'city', 'province', 'country', 'zip_code', 'home_phone', 'work_phone', 'email']

            writer = csv.writer(response)
            writer.writerow(export_header_names)

            #for row in self.object_list:
            #    writer.writerow([row.first_name, row.last_name, row.address, row.city, row.province, row.country, row.zip_code, row.home_phone, row.work_phone, row.email])
            return response

        if request.POST.get('bulk_delete'):
            self.object_list = self.get_queryset()

            if 'delete_all' in request.POST:
                delete_list = self.object_list.values_list('id', flat=True)
            else:   
                delete_list = request.POST.getlist('multi_delete')

            for each_id in delete_list:
                Quote.objects.get(id=each_id).delete()

            return redirect("quotes:quote-list")

        if request.POST.get('bulk_deactivate'):
            self.object_list = self.get_queryset()

            if 'delete_all' in request.POST:
                deactivate_list = self.object_list.values_list('id', flat=True)
            else:   
                deactivate_list = request.POST.getlist('multi_delete')

            for each_id in deactivate_list:
                Quote.objects.filter(id=each_id).update(active='NO')

            return redirect("quotes:quote-list")


class QuoteCreateView(LoginRequiredMixin, generic.CreateView):
    model = Quote
    template_name = "quotes/quote_create.html"
    form_class = QuoteModelForm

    def get_context_data(self, **kwargs):
        context = super(QuoteCreateView, self).get_context_data(**kwargs)
         
        if self.request.POST:
            context['form'] = QuoteModelForm(self.request.POST)

        else:
            context['form'] = QuoteModelForm()
            
        return context

    def get_success_url(self):
        return reverse("quotes:quote-list")


class QuoteUpdateView(LoginRequiredMixin, generic.UpdateView):    
    model = Quote
    template_name = "quotes/quote_update.html"
    form_class = QuoteProductForm

    def get_context_data(self, **kwargs):
        context = super(QuoteUpdateView, self).get_context_data(**kwargs)
        quote = Quote.objects.get(pk=self.kwargs.get('pk'))
        
        if self.request.POST:
            context['product_select'] = QuoteProductForm(self.request.POST, instance=quote)
            context['product_list'] = QuoteProducts.objects.filter(quote_id=self.kwargs['pk'])

            cart_quantity_list = QuoteProducts.objects.filter(quote_id=self.kwargs['pk']).values_list('product_quantity',flat=True)
            cart_price_list = QuoteProducts.objects.filter(quote_id=self.kwargs['pk']).values_list('product_price',flat=True)

            row_total_list = [a*b for a,b in zip(cart_quantity_list,cart_price_list)]
            sub_total = sum(row_total_list)
            
            context['sub_total'] = sub_total

        else:
            context['product_select'] = QuoteProductForm(instance=quote)
            context['product_list'] = QuoteProducts.objects.filter(quote_id=self.kwargs['pk'])

            cart_quantity_list = QuoteProducts.objects.filter(quote_id=self.kwargs['pk']).values_list('product_quantity',flat=True)            
            cart_price_list = QuoteProducts.objects.filter(quote_id=self.kwargs['pk']).values_list('product_price',flat=True)

            row_total_list = [a*b for a,b in zip(cart_quantity_list,cart_price_list)]
            sub_total = sum(row_total_list)

            context['sub_total'] = sub_total
           
        return context


    def post(self, request, *args, **kwargs):
        invoice = Invoice
        quote = Quote.objects.get(pk=self.kwargs.get('pk'))

        if request.method=='POST' and 'add_cart' in request.POST:
            current_selection = request.POST['product_select']
            current_quantity = request.POST['product_quantity']
            current_price = Product.objects.filter(id=current_selection).values_list('sell_price',flat=True)
            
            new_entry = QuoteProducts(quote_id=self.kwargs.get('pk'), product_select_id=current_selection, product_quantity=current_quantity, product_price=current_price)
            new_entry.save()

            return HttpResponseRedirect(self.request.path_info)

        if request.method=='POST' and 'multi_delete' in request.POST:
            delete_list = request.POST.getlist('multi_delete')

            for each_id in delete_list:
                QuoteProducts.objects.get(id=each_id).delete()

            return HttpResponseRedirect(self.request.path_info)


        if request.method=='POST' and 'add_to_invoice' in request.POST:
            
            invoice_entry = Invoice(quote_id=self.kwargs.get('pk'),
                                invoice_first_name=quote.customer.first_name,
                                invoice_last_name=quote.customer.last_name,
                                invoice_address=quote.customer.address,
                                invoice_zip_code=quote.customer.zip_code,
                                invoice_home_phone=quote.customer.home_phone,
                                invoice_quote_key=self.kwargs.get('pk'),)
                                #invoice_product_select=current_selection,
                                #invoice_product_quantity=current_quantity,
                                #invoice_product_price=current_price, )
                                #invoice_product_quantity='1',
                                #invoice_product_price='1')
            
            invoice_entry.save()

            #return HttpResponseRedirect(self.request.path_info)
            return redirect("quotes:quote-list")


        return redirect("quotes:quote-list")
        
    def get_success_url(self):
        return reverse("quotes:quote-list")


    def form_valid(self, form):
        form.instance.quote_id = self.kwargs['pk']
        form.instance.save()
        return super(QuoteUpdateView, self).form_valid(form)


    def form_invalid(self, **kwargs):
        return self.render_to_response(self.get_context_data(**kwargs))

class QuoteDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Quote
    template_name = "quotes/quote_delete.html"

    def get_success_url(self):
        return reverse("quotes:quote-list")

class QuoteListNote(LoginRequiredMixin, generic.CreateView):
    template_name = "quotes/quote_list_note.html"
    form_class = QuoteNoteForm

    def get_context_data(self, **kwargs):        
        context = super(QuoteListNote, self).get_context_data(**kwargs)
        context['object_list'] = int(Quote.objects.filter(id=self.kwargs['pk']).values_list('id',flat=True)[0])      
        context['note_list'] = QuoteNotes.objects.filter(quote_id=self.kwargs['pk'])
        
        try:
            context['note_update_list'] = list(QuoteNotes.objects.filter(author_id=self.request.user.id, quote_id=self.kwargs['pk']).values_list('id',flat=True))
        except IndexError:
            pass

        return context

    def form_valid(self, form):
        form.instance.author_id = self.request.user.id
        form.instance.quote_id = self.kwargs['pk']
        return super(QuoteListNote, self).form_valid(form)

    def get_success_url(self):
        return self.request.path

class QuoteDeleteNote(LoginRequiredMixin, generic.DeleteView):
    model = QuoteNotes
    template_name = "quotes/quote_delete_note.html"

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author_id != self.request.user.id:
            raise PermissionDenied("User can't delete this question.")
        return super(QuoteDeleteNote, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("quotes:quote-list")

class QuoteUploadView(LoginRequiredMixin, generic.ListView):
    template_name = "quotes/quote_upload.html"
    queryset = Quote.objects.all()
    
    def post(self, request, *args, **kwargs):
        
        header_original = ['first_name', 'last_name', 'address', 'city', 'province', 'country', 'zip_code', 'home_phone', 'work_phone', 'email']
        header_count = len(header_original)

        if request.POST.get('import_csv'):

            csv_file = request.FILES['file']

            # Check if file ends with csv
            if csv_file.name.endswith('.csv'):
                df_model_test = pd.DataFrame(list(Quote.objects.all().values('id')))

            else:
                messages.info(request, 'File format is not .csv')
                return render(request, "quotes/quote_upload.html", {}) 

            # Check for keys from existing data            
            if not df_model_test.empty:
                df_from_model_id = df_model_test
                df_from_model_id_filtered = df_from_model_id['id'].values.tolist()
                df_from_model = pd.DataFrame(list(Supplier.objects.all().values('first_name', 'last_name', 'home_phone')))
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
                return render(request, "quotes/quote_upload.html", {}) 
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
                        Quote.objects.filter(id = x).update(address=y)

                if 'city' in df_update.columns:
                    city = df_update['city']
                    for x, y in zip(pk_numbers, city):
                        Quote.objects.filter(id = x).update(city=y)

                if 'province' in df_update.columns:
                    province = df_update['province']
                    for x, y in zip(pk_numbers, province):
                        Quote.objects.filter(id = x).update(province=y)

                if 'country' in df_update.columns:
                    country = df_update['country']
                    for x, y in zip(pk_numbers, country):
                        Quote.objects.filter(id = x).update(country=y)

                if 'zip_code' in df_update.columns:
                    zip_code = df_update['zip_code']
                    for x, y in zip(pk_numbers, zip_code):
                        Quote.objects.filter(id = x).update(zip_code=y)

                if 'work_phone' in df_update.columns:
                    work_phone = df_update['work_phone']
                    for x, y in zip(pk_numbers, work_phone):
                        Quote.objects.filter(id = x).update(work_phone=y)

                if 'email' in df_update.columns:
                    email = df_update['email']
                    for x, y in zip(pk_numbers, email):
                        Quote.objects.filter(id = x).update(email=y)

                if 'active' in df_update.columns:
                    active = df_update['active']
                    for x, y in zip(pk_numbers, active):
                        Quote.objects.filter(id = x).update(active=y)

                # This section adds new records after update the exisiting records
                if len(diff_positions) != 0:
                    df_create = df.iloc[diff_positions,:]            
                    row_iter_create = df_create.iterrows()

                    try:
                        objs = [
                            Quote(
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

                        Quote.objects.bulk_create(objs)
                        messages.info(request, 'Woohoo both update and import successful! ' + str(len(diff_positions)) + ' records are added')
                        return render(request, "quotes/quote_upload.html", {})
                    
                    except Exception as e:
                        messages.info(request, 'For new upload please make sure all headers are in csv file and follow the template. Use (first_name, last_name, address...) make sure spelling and _ are correct.')
                        return render(request, "quotes/quote_upload.html", {})
  
                messages.info(request, 'Hooray update successful! ' + str(len(match_positions)) + ' records are updated')
                return render(request, "quotes/quote_upload.html", {})

            if len(diff_positions) != 0:
                df_create = df.iloc[diff_positions,:]            
                row_iter_create = df_create.iterrows()

                try:
                    objs = [
                        Quote(
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

                    Quote.objects.bulk_create(objs)
                    messages.info(request, 'Yay import successful! ' + str(len(diff_positions)) + ' records are added')
                    return render(request, "quotes/quote_upload.html", {})
                
                except Exception as e:
                    messages.info(request, 'For new upload please make sure all headers are in csv file and follow the template. Use (first_name, last_name, address...) make sure spelling and _ are correct.')
                    return render(request, "quotes/quote_upload.html", {})
            else:
                messages.info(request, 'No update or import was found!')
                return render(request, "quotes/quote_upload.html", {})
