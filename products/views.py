import csv, io
import pandas as pd
from django.contrib import messages
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from .models import Product, ProductNotes, ProductReviews
from .forms import ProductModelForm, ProductNoteForm, ProductReviewForm


class ProductListView(LoginRequiredMixin, generic.ListView):    
    template_name = "products/product_list.html"
    paginate_by = 50
    ordering = ['product_code']

    def get_paginate_by(self, queryset):
        return self.request.GET.get('paginate_by', self.paginate_by)

    def get_ordering(self):
        self.order = self.request.GET.get('order', 'asc')
        selected_ordering = self.request.GET.get('ordering', '-date_added')
        if self.order == "desc":
            selected_ordering = "-" + selected_ordering
        return selected_ordering

    def get_context_data(self, *args, **kwargs):
        context = super(ProductListView, self).get_context_data(*args, **kwargs)
        context['current_order'] = self.get_ordering()
        context['order'] = self.order
        context['active_list'] = Product.objects.filter(active="YES")
        context['none_active_list'] = Product.objects.filter(active="NO")
        return context

    def get_queryset(self, query=None):
        query = self.request.GET.get('q')
        active_filter = self.request.GET.get('active')
        ordering = self.get_ordering()

        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        if query:
            object_list = Product.objects.filter(active=active_filter) & Product.objects.filter(
                Q(product_code__icontains=query) |
                Q(internal_code__icontains=query) |
                Q(product_title__icontains=query) |
                Q(part_number__icontains=query) |
                Q(brand_name__icontains=query) |
                Q(date_added__icontains=query) |
                Q(upc__icontains=query)
                ).order_by(ordering)

        elif start_date and end_date:
            object_list = Product.objects.filter(active=active_filter) & Product.objects.filter(
                Q(product_code__icontains=query) |
                Q(internal_code__icontains=query) |
                Q(product_title__icontains=query) |
                Q(part_number__icontains=query) |
                Q(brand_name__icontains=query) |
                Q(date_added__icontains=query) |
                Q(upc__icontains=query)
                ).filter(date_added__range=(start_date, end_date))
            
        elif active_filter=="NO":
            object_list = Product.objects.all().filter(active="NO").order_by(ordering)
            
        else:
            object_list = Product.objects.all().filter(active="YES").order_by(ordering)
   
        return object_list

    def post(self, request, *args, **kwargs):
        if request.POST.get('export_csv'):
            self.object_list = self.get_queryset()
            
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment;filename=export_product.csv'

            # opts = queryset.model._meta
            export_header_names = ['product_code', 'brand_name', 'internal_code', 'upc', 'product_title', 'product_description', 'sell_price', 'cost_price', 'inventory_count']

            writer = csv.writer(response)
            writer.writerow(export_header_names)

            for row in self.object_list:
                writer.writerow([row.product_code, row.brand_name, row.internal_code, row.upc, row.product_title, row.product_description, row.sell_price, row.cost_price, row.inventory_count])
            return response

        if request.POST.get('bulk_delete'):
            self.object_list = self.get_queryset()

            if 'delete_all' in request.POST:
                delete_list = self.object_list.values_list('id', flat=True)
            else:   
                delete_list = request.POST.getlist('multi_delete')

            for each_id in delete_list:
                Product.objects.get(id=each_id).delete()

            return redirect("products:product-list")

        if request.POST.get('bulk_deactivate'):
            self.object_list = self.get_queryset()

            if 'delete_all' in request.POST:
                deactivate_list = self.object_list.values_list('id', flat=True)
            else:   
                deactivate_list = request.POST.getlist('multi_delete')

            for each_id in deactivate_list:
                Product.objects.filter(id=each_id).update(active='NO')

            return redirect("products:product-list")


class ProductUploadView(LoginRequiredMixin, generic.ListView):
    template_name = "products/product_upload.html"
    queryset = Product.objects.all()
    
    def post(self, request, *args, **kwargs):
        
        header_original = ['product_code', 'brand_name', 'brand_family', 'internal_code', 'upc', 'part_number', 'product_title', 'product_description', 'sell_price', 'cost_price', 'inventory_count', 'product_material', 'product_color', 'product_length', 'product_width', 'product_height', 'product_volume', 'product_weight', 'product_image_one', 'product_image_two', 'product_image_three', 'product_image_four', 'product_image_five']
        header_count = len(header_original)


        if request.POST.get('import_csv'):

            csv_file = request.FILES['file']

            # Check if file ends with csv
            if csv_file.name.endswith('.csv'):
                df_model_test = pd.DataFrame(list(Product.objects.all().values('id')))
                print(df_model_test)

            else:
                messages.info(request, 'File format is not .csv')
                return render(request, "products/product_upload.html", {}) 

            # Check for keys from existing data            
            if not df_model_test.empty:
                df_from_model_id = df_model_test
                df_from_model_id_filtered = df_from_model_id['id'].values.tolist()
                df_from_model = pd.DataFrame(list(Product.objects.all().values('product_code')))
                df_from_model.applymap(lambda x: x.strip() if isinstance(x, str) else x)                       
                df_from_model_key = list(df_from_model['product_code'])
                           
            else:
                df_from_model_key = []

            df = pd.read_csv(csv_file)
            df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

            # Check if columns contain key info
            if 'product_code' in df.columns:
                lead_keys = True
            else:
                messages.info(request, 'Headers missing, key columns product_code is missing.')
                return render(request, "products/product_upload.html", {}) 
                lead_keys = False

            df_from_csv = df[['product_code']]
            df_from_csv_key = list(df_from_csv['product_code'])

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
                df_update_all = df_update[['product_code']]

                for each in match_id:
                    pk_numbers.append(df_from_model_id_filtered[each])

                if 'brand_name' in df_update.columns:
                    brand_name = df_update['brand_name'].tolist()                    
                    for x, y in zip(pk_numbers, brand_name):
                        Product.objects.filter(id = x).update(brand_name=y)

                if 'brand_family' in df_update.columns:
                    brand_family = df_update['brand_family']
                    for x, y in zip(pk_numbers, brand_family):
                        Product.objects.filter(id = x).update(brand_family=y)

                if 'internal_code' in df_update.columns:
                    internal_code = df_update['internal_code']
                    for x, y in zip(pk_numbers, internal_code):
                        Product.objects.filter(id = x).update(internal_code=y)

                if 'upc' in df_update.columns:
                    upc = df_update['upc']
                    for x, y in zip(pk_numbers, upc):
                        Product.objects.filter(id = x).update(upc=y)

                if 'part_number' in df_update.columns:
                    part_number = df_update['part_number']
                    for x, y in zip(pk_numbers, part_number):
                        Product.objects.filter(id = x).update(part_number=y)

                if 'product_title' in df_update.columns:
                    product_title = df_update['product_title']
                    for x, y in zip(pk_numbers, product_title):
                        Product.objects.filter(id = x).update(product_title=y)

                if 'product_description' in df_update.columns:
                    product_description = df_update['product_description']
                    for x, y in zip(pk_numbers, product_description):
                        Product.objects.filter(id = x).update(product_description=y)

                if 'sell_price' in df_update.columns:
                    sell_price = df_update['sell_price']
                    for x, y in zip(pk_numbers, sell_price):
                        Product.objects.filter(id = x).update(sell_price=y)

                if 'cost_price' in df_update.columns:
                    cost_price = df_update['cost_price']
                    for x, y in zip(pk_numbers, cost_price):
                        Product.objects.filter(id = x).update(cost_price=y)

                if 'inventory_count' in df_update.columns:
                    inventory_count = df_update['inventory_count']
                    for x, y in zip(pk_numbers, inventory_count):
                        Product.objects.filter(id = x).update(inventory_count=y)

                if 'product_material' in df_update.columns:
                    product_material = df_update['product_material']
                    for x, y in zip(pk_numbers, product_material):
                        Product.objects.filter(id = x).update(product_material=y)
                        
                if 'product_color' in df_update.columns:
                    product_color = df_update['product_color']
                    for x, y in zip(pk_numbers, product_color):
                        Product.objects.filter(id = x).update(product_color=y)

                if 'product_length' in df_update.columns:
                    product_length = df_update['product_length']
                    for x, y in zip(pk_numbers, product_length):
                        Product.objects.filter(id = x).update(product_length=y)

                if 'product_width' in df_update.columns:
                    product_width = df_update['product_width']
                    for x, y in zip(pk_numbers, product_width):
                        Product.objects.filter(id = x).update(product_width=y)

                if 'product_height' in df_update.columns:
                    product_height = df_update['product_height']
                    for x, y in zip(pk_numbers, product_height):
                        Product.objects.filter(id = x).update(product_height=y)

                if 'product_volume' in df_update.columns:
                    product_volume = df_update['product_volume']
                    for x, y in zip(pk_numbers, product_volume):
                        Product.objects.filter(id = x).update(product_volume=y)

                if 'product_weight' in df_update.columns:
                    product_weight = df_update['product_weight']
                    for x, y in zip(pk_numbers, product_weight):
                        Product.objects.filter(id = x).update(product_weight=y)

                if 'product_image_one' in df_update.columns:
                    product_image_one = df_update['product_image_one']
                    for x, y in zip(pk_numbers, product_image_one):
                        Product.objects.filter(id = x).update(product_image_one=y)

                if 'product_image_two' in df_update.columns:
                    product_image_two = df_update['product_image_two']
                    for x, y in zip(pk_numbers, product_image_two):
                        Product.objects.filter(id = x).update(product_image_two=y)

                if 'product_image_three' in df_update.columns:
                    product_image_three = df_update['product_image_three']
                    for x, y in zip(pk_numbers, product_image_three):
                        Product.objects.filter(id = x).update(product_image_three=y)

                if 'product_image_four' in df_update.columns:
                    product_image_four = df_update['product_image_four']
                    for x, y in zip(pk_numbers, product_image_four):
                        Product.objects.filter(id = x).update(product_image_four=y)

                if 'product_image_five' in df_update.columns:
                    product_image_five = df_update['product_image_five']
                    for x, y in zip(pk_numbers, product_image_five):
                        Product.objects.filter(id = x).update(product_image_five=y)

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
                            Product(
                                product_code = row['product_code'],
                                brand_name = row['brand_name'],
                                #brand_family = row['brand_family'],
                                #internal_code = row['internal_code'],
                                upc = row['upc'],
                                #part_number = row['part_number'],
                                product_title = row['product_title'],
                                product_description = row['product_description'],
                                sell_price = row['sell_price'],
                                cost_price = row['cost_price'],
                                inventory_count  = row['inventory_count'],
                                product_weight = row['product_weight'],
                            )
                            for index, row in row_iter_create
                        ]

                        Product.objects.bulk_create(objs)
                        messages.info(request, 'Woohoo both update and import successful! ' + str(len(diff_positions)) + ' records are added')
                        return render(request, "products/product_upload.html", {})
                    
                    except Exception as e:
                        messages.info(request, 'For new upload please make sure all headers are in csv file and follow the template. Use (product_code, upc, product_title...) make sure spelling and _ are correct.')
                        return render(request, "products/product_upload.html", {})
                        
                messages.info(request, 'Hooray update successful! ' + str(len(match_positions)) + ' records are updated')
                return render(request, "products/product_upload.html", {})

            if len(diff_positions) != 0:
                df_create = df.iloc[diff_positions,:]            
                row_iter_create = df_create.iterrows()

                try:
                    objs = [
                        Product(
                            product_code = row['product_code'],
                            brand_name = row['brand_name'],
                            #brand_family = row['brand_family'],
                            #internal_code = row['internal_code'],
                            upc = row['upc'],
                            #part_number = row['part_number'],
                            product_title = row['product_title'],
                            product_description = row['product_description'],
                            sell_price = row['sell_price'],
                            cost_price = row['cost_price'],
                            inventory_count  = row['inventory_count'],
                            product_weight = row['product_weight'],
                        )
                        for index, row in row_iter_create
                    ]

                    Product.objects.bulk_create(objs)
                    messages.info(request, 'Yay import successful! ' + str(len(diff_positions)) + ' records are added')
                    return render(request, "products/product_upload.html", {})
                
                except Exception as e:
                    messages.info(request, 'For new upload please make sure all headers are in csv file and follow the template. Use (product_code, upc, product_title...) make sure spelling and _ are correct.')
                    return render(request, "products/product_upload.html", {})
            else:
                messages.info(request, 'No update or import was found!')
                return render(request, "products/product_upload.html", {})

class ProductCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = "products/product_create.html"
    form_class = ProductModelForm

    def get_success_url(self):
        return reverse("products:product-list")

    def form_valid(self, form):
        return super(ProductCreateView, self).form_valid(form)

class ProductUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Product
    template_name = "products/product_update.html"
    form_class = ProductModelForm
            
    def get_success_url(self):
        return reverse("products:product-list")

class ProductDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Product
    template_name = "products/product_delete.html"

    def get_success_url(self):
        return reverse("products:product-list")

class ProductListNote(LoginRequiredMixin, generic.CreateView):
    template_name = "products/product_list_note.html"
    form_class = ProductNoteForm

    def get_context_data(self, **kwargs):        
        context = super(ProductListNote, self).get_context_data(**kwargs)
        context['object_list'] = int(Product.objects.filter(id=self.kwargs['pk']).values_list('id',flat=True)[0])      
        context['note_list'] = ProductNotes.objects.filter(product_id=self.kwargs['pk'])
        
        try:
            context['note_update_list'] = list(ProductNotes.objects.filter(author_id=self.request.user.id, product_id=self.kwargs['pk']).values_list('id',flat=True))
        except IndexError:
            pass

        return context

    def form_valid(self, form):
        form.instance.author_id = self.request.user.id
        form.instance.product_id = self.kwargs['pk']
        return super(ProductListNote, self).form_valid(form)

    def get_success_url(self):
        return self.request.path

class ProductDeleteNote(LoginRequiredMixin, generic.DeleteView):
    model = ProductNotes
    template_name = "products/product_delete_note.html"

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author_id != self.request.user.id:
            raise PermissionDenied("User can't delete this question.")
        return super(ProductDeleteNote, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("products:product-list")

class ProductListReview(LoginRequiredMixin, generic.CreateView):
    template_name = "products/product_list_review.html"
    form_class = ProductReviewForm
    
    def get_context_data(self, **kwargs):
        context = super(ProductListReview, self).get_context_data(**kwargs)
        context['object_list'] = int(Product.objects.filter(id=self.kwargs['pk']).values_list('id',flat=True)[0])
        context['review_list'] = ProductReviews.objects.filter(product_id=self.kwargs['pk'])
        
        try:
            context['review_update_list'] = list(ProductReviews.objects.filter(author_id=self.request.user.id, product_id=self.kwargs['pk']).values_list('id',flat=True))
        except IndexError:
            pass
        
        return context

    def form_valid(self, form):
        form.instance.author_id = self.request.user.id
        form.instance.product_id = self.kwargs['pk']
        return super(ProductListReview, self).form_valid(form)

    def get_success_url(self):
        return self.request.path

class ProductDeleteReview(LoginRequiredMixin, generic.DeleteView):
    model = ProductReviews
    template_name = "products/product_delete_review.html"

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author_id != self.request.user.id:
            raise PermissionDenied("User can't delete this question.")
        return super(ProductDeleteReview, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("products:product-list")
