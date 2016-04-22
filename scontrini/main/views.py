from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms.models import ModelForm

from .models import Receipt



class MainView(TemplateView):
    template_name = "main.html"


class ReceiptForm(ModelForm):
    class Meta(object):
        model = Receipt
        fields = []


class UploadView(LoginRequiredMixin, View):
    def post(self, request):
        print(request.POST)
