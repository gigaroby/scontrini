from django.db import models
from django.contrib.auth.models import User
from jsonfield import JSONField


class Receipt(models.Model):
    owner = models.ForeignKey(to=User)

    image = models.ImageField()
    receipt_data = JSONField(blank=True)
    completed = models.BooleanField(default=False)

    name = models.CharField(max_length=200, null=True, blank=True)
    category = models.CharField(max_length=200, null=True, blank=True)
    price = models.FloatField(null=True)
    notes = models.TextField(max_length=10000, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return '/edit/{}'.format(self.pk)
