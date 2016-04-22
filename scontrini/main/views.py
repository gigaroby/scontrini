import io
import time
import json
import base64

from django.core.files import File
from django.http import HttpResponse
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms.models import ModelForm
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView

from .models import Receipt


class MainView(TemplateView):
    template_name = "main.html"


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
    required_fields = ['name', 'category', 'price']

    class Meta:
        model = Receipt
        fields = ['name', 'category', 'price', 'notes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.required_fields:
            self.fields[field].required = True


class ReceiptUpdate(UpdateView):
    model = Receipt
    form_class = ReceiptUpdateForm
    template_name_suffix = '_update_form'


class ReceiptListView(ListView):
    model = Receipt


class StatisticsView(TemplateView):
    template_name = "main/statistics.html"

    def get_context_data(self, **kwargs):
        from collections import Counter
        c = Counter()
        for r in Receipt.objects.all():
            c[r.category] += 1
        total = len(c)

        data = [{
            "name": 'Categories',
            "colorByPoint": True,
            "data": [{
                "name": name,
                "y": (amount/total)*100
            } for name, amount in c.items()]
        }];
        return {'data': json.dumps(data), 'caption': 'Categorie di acquisto'}
