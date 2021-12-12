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

from .models import Invoice, InvoiceNotes

from .forms import InvoiceNoteForm


class InvoiceListView(LoginRequiredMixin, generic.ListView):
    template_name = "invoices/invoice_list.html"
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
        context = super(InvoiceListView, self).get_context_data(*args, **kwargs)
        context['current_order'] = self.get_ordering()
        context['order'] = self.order
        context['active_list'] = Invoice.objects.all()
        return context

    def get_queryset(self, query=None):
        query = self.request.GET.get('q')
        active_filter = self.request.GET.get('active')
        ordering = self.get_ordering()
        
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        if query:                
            object_list = Invoice.objects.filter(
                Q(invoice_first_name__icontains=query) |
                Q(invoice_last_name__icontains=query) |
                Q(invoice_address__icontains=query)).order_by(ordering)

        elif start_date and end_date:
            object_list = Invoice.objects.filter(
                Q(invoice_first_name__icontains=query) |
                Q(invoice_last_name__icontains=query) |
                Q(invoice_address__icontains=query)).filter(date_added__range=(start_date, end_date))
         
        elif active_filter=="NO":
            object_list = Invoice.objects.all().order_by(ordering)
            
        else:
            object_list = Invoice.objects.all().order_by(ordering)
   
        return object_list


    def post(self, request, *args, **kwargs):
        if request.POST.get('export_csv'):
            self.object_list = self.get_queryset()
            
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment;filename=export_invoices.csv'

            export_header_names = ['invoice_first_name', 'invoice_last_name', 'invoice_address', 'invoice_zip_code', 'invoice_home_phone']

            writer = csv.writer(response)
            writer.writerow(export_header_names)

            for row in self.object_list:
                writer.writerow([row.invoice_first_name, row.invoice_last_name, row.invoice_address, row.invoice_zip_code, row.invoice_home_phone])
            return response


class InvoiceDetailView(LoginRequiredMixin, generic.DetailView):    
    model = Invoice
    template_name = "invoices/invoice_detail.html"

    def get_context_data(self, *args, **kwargs):
        context = super(InvoiceDetailView, self).get_context_data(**kwargs)
        quote_key = Invoice.objects.get(pk=self.kwargs.get('pk'))
        
        context['invoice'] = Invoice.objects.get(pk=self.kwargs.get('pk'))
        context['product_list'] = QuoteProducts.objects.filter(quote_id=quote_key.quote_id)
        return context

class InvoiceListNote(LoginRequiredMixin, generic.CreateView):
    template_name = "invoices/invoice_list_note.html"
    form_class = InvoiceNoteForm

    def get_context_data(self, **kwargs):        
        context = super(InvoiceListNote, self).get_context_data(**kwargs)
        context['object_list'] = int(Invoice.objects.filter(id=self.kwargs['pk']).values_list('id',flat=True)[0])      
        context['note_list'] = InvoiceNotes.objects.filter(invoice_id=self.kwargs['pk'])
        
        try:
            context['note_update_list'] = list(InvoiceNotes.objects.filter(author_id=self.request.user.id, invoice_id=self.kwargs['pk']).values_list('id',flat=True))
        except IndexError:
            pass

        return context

    def form_valid(self, form):
        form.instance.author_id = self.request.user.id
        form.instance.invoice_id = self.kwargs['pk']
        return super(InvoiceListNote, self).form_valid(form)

    def get_success_url(self):
        return self.request.path

class InvoiceDeleteNote(LoginRequiredMixin, generic.DeleteView):
    model = InvoiceNotes
    template_name = "invoices/invoice_delete_note.html"

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author_id != self.request.user.id:
            raise PermissionDenied("User can't delete this question.")
        return super(InvoiceDeleteNote, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("invoices:invoice-list")
