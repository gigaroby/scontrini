import io
import time
import json
import base64

from django.core.files import File
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms.models import ModelForm
from django.forms import HiddenInput
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, FormView
from django.views.generic.list import ListView

from .models import Receipt, map_categories, CATEGORIES


class ReceiptForm(ModelForm):
    class Meta(object):
        model = Receipt
        fields = []


class UploadView(LoginRequiredMixin, View):
    def post(self, request):
        remove = 'imgData=data:image/png;base64,'
        image_base64 = request.body[len(remove):]
        image_data = io.BytesIO(base64.b64decode(image_base64))

        new_receipt = Receipt()
        new_receipt.owner = request.user
        new_receipt.image.save('{}.png'.format(time.monotonic()), File(image_data))
        new_receipt.save()

        return HttpResponse(new_receipt.id)


class ReceiptUpdateForm(ModelForm):
    required_fields = ['category', 'price']

    class Meta:
        model = Receipt
        fields = ['shop', 'category', 'price', 'notes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.required_fields:
            self.fields[field].required = True


class ReceiptUpdate(UpdateView):
    model = Receipt
    form_class = ReceiptUpdateForm
    template_name_suffix = '_update_form'

    def form_valid(self, form):
        out = super().form_valid(form)
        form.instance.completed = True
        form.instance.save()

        return out



class ReceiptListView(ListView):

    queryset = Receipt.objects.filter(completed=True)

    def get_queryset(self):
        q = self.request.GET.get('q')
        cat = self.request.GET.get('cat')
        qs = super().get_queryset()

        if q:
            qs = qs.filter(Q(shop__icontains=q) | Q(notes__icontains=q))

        if cat:
            qs = qs.filter(category=cat)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['categories'] = CATEGORIES
        context['selected_category'] = self.request.GET.get('cat')

        return context


class StatisticsView(TemplateView):
    template_name = "main/statistics.html"

    def get_context_data(self, **kwargs):
        from collections import Counter
        c = Counter()
        for r in Receipt.objects.filter(completed=True):
            c[r.category] += 1
        total = len(c)

        data = [{
            "name": 'Categories',
            "colorByPoint": True,
            "data": [{
                "name": name,
                "y": (amount/total)*100
            } for name, amount in c.items()]
        }]
        return {'data': json.dumps(data), 'caption': 'Categorie di acquisto'}


class ReceiptCreateForm(ModelForm):
    class Meta:
        model = Receipt
        fields = ['image', 'has_position', 'lat', 'long']
        widgets = {
            'lat': HiddenInput(),
            'long': HiddenInput(),
            'has_position': HiddenInput(),
        }


class ReceiptNewView(FormView):
    template_name = 'main/receipt_create_form.html'
    form_class = ReceiptCreateForm

    def get_success_url(self):
        return reverse('select-receipt', kwargs={'pk': self.obj.id})

    def form_valid(self, form):
        self.obj = form.save(commit=False)
        self.obj.owner = self.request.user
        self.obj.save()
        return super().form_valid(form)


class ReceiptDetail(DetailView):
    model = Receipt


class ReceiptShopSelect(UpdateView):
    template_name = 'main/shop_select.html'
    model = Receipt
    fields = ['selected_shop', 'selected_price']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        self.object.fetch_shops()

        context['object'] = self.object

        return context

    def form_valid(self, form):
        out = super().form_valid(form)

        obj = self.object
        selected = obj.receipt_data[obj.selected_shop]
        obj.shop = selected['label']
        obj.category = map_categories(selected['ateco_code'])
        obj.price = obj.price_list[obj.selected_price]
        obj.save()

        return out

