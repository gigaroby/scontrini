from django.db import models
from django.contrib.auth.models import User
from jsonfield import JSONField


class Receipt(models.Model):
    owner = models.ForeignKey(to=User)

    image = models.ImageField()
    receipt_data = JSONField(blank=True)

    created = models.DateTimeField(auto_now_add=True)

