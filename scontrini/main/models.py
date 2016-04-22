from django.db import models
from django.contrib.auth.models import User
from jsonfield import JSONField
from scontrini.ocr.ocr import OcrReceipt
from .ateco import ateco_to_category, get_categories



CATEGORIES = [(c, c) for c in get_categories()]



def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}'.format(instance.owner.id, filename)


def map_categories(ateco):
    return ateco_to_category(ateco)


class Receipt(models.Model):
    owner = models.ForeignKey(to=User)

    image = models.ImageField(upload_to=user_directory_path)
    receipt_data = JSONField(blank=True)
    selected_shop = models.IntegerField(null=True)
    completed = models.BooleanField(default=False)

    name = models.CharField(max_length=200, null=True, blank=True)
    shop = models.CharField(max_length=400, null=True, blank=True)
    category = models.CharField(max_length=200, null=True, blank=True, choices=CATEGORIES)
    price_list = JSONField(blank=True)
    price = models.FloatField(null=True)
    selected_price = models.IntegerField(null=True)
    notes = models.TextField(max_length=10000, null=True, blank=True)

    has_position = models.BooleanField(default=False)
    lat = models.FloatField(verbose_name='latitude', blank=True, null=True)
    long = models.FloatField(verbose_name='longitude', blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "<Receipt owner={} created={}>".format(self.owner.username, self.created)

    def get_absolute_url(self):
        return '/edit/{}'.format(self.pk)

    def fetch_shops(self):
        if self.receipt_data != '':
            return

        l = OcrReceipt(self.image.path)
        l.parse()

        self.receipt_data = l.companies
        self.price_list = l.totals
        self.save()

    def get_icon(self):
        icons = {'Affitto': 'home',
                 'Bollette': 'envelope',
                 'Alberghi e ristoranti': 'cutlery',
                 'Altro': 'gift',
                 'Automobile':'road',
                 'Intrattenimento': 'play',
                 'Spesa': 'shopping-cart',
                 'Vestiti': 'scissors'}
        return icons.get(self.category, 'eur')
