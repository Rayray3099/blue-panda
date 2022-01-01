from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from django.http import HttpResponseRedirect

from django.shortcuts import render
from django.http import JsonResponse

from leads.models import Lead
from products.models import Product
from quotes.models import Quote
from scheduler.models import Schedule

class Reports(LoginRequiredMixin, generic.TemplateView):
    template_name = "reports/report.html"

    def get_context_data(self, *args, **kwargs):
        context = super(Reports, self).get_context_data(*args, **kwargs)
        
        context['leads_chart'] = Lead.objects.all()
        context['products_chart'] = Product.objects.all()
        context['quotes_chart'] = Quote.objects.all()
        context['schedules_chart'] = Schedule.objects.all()
        
        return context
