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

        if query:
            object_list = Invoice.objects.filter(active=active_filter) & Quote.objects.filter(
                Q(customer__icontains=query) |
                Q(products__icontains=query) |
                Q(quote_id__icontains=query))
            
        elif active_filter=="NO":
            object_list = Invoice.objects.all()
            
        else:
            object_list = Invoice.objects.all()
   
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


class InvoiceDetailView(LoginRequiredMixin, generic.DetailView):    
    model = Invoice
    template_name = "invoices/invoice_detail.html"

    def get_context_data(self, *args, **kwargs):
        context = super(InvoiceDetailView, self).get_context_data(**kwargs)
        quote_key = Invoice.objects.get(pk=self.kwargs.get('pk'))
        
        context['invoice'] = Invoice.objects.get(pk=self.kwargs.get('pk'))
        context['product_list'] = QuoteProducts.objects.filter(quote_id=quote_key.quote_id)
        return context
