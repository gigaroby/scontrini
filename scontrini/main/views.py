import io
import time
import base64

from django.core.files import File
from django.http import HttpResponse
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
        remove = 'imgData=data:image/png;base64,'
        image_base64 = request.body[len(remove):]
        image_data = io.BytesIO(base64.b64decode(image_base64))

        new_receipt = Receipt()
        new_receipt.owner = request.user
        new_receipt.image.save('{}.png'.format(time.monotonic()), File(image_data))
        new_receipt.save()

        return HttpResponse(new_receipt.id)
