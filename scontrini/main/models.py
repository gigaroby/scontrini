from django.db import models
from django.contrib.auth.models import User
from jsonfield import JSONField


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}'.format(instance.owner.id, filename)


def map_categories(ateco):
    return CATEGORIES[len(ateco) % len(CATEGORIES)]


CATEGORIES = [(c, c) for c in ['Alimentari', 'Benzina']]


class Receipt(models.Model):
    owner = models.ForeignKey(to=User)

    image = models.ImageField(upload_to=user_directory_path)
    receipt_data = JSONField(blank=True)
    completed = models.BooleanField(default=False)

    name = models.CharField(max_length=200, null=True, blank=True)
    category = models.CharField(max_length=200, null=True, blank=True, choices=CATEGORIES)
    price = models.FloatField(null=True)
    notes = models.TextField(max_length=10000, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "<Receipt owner={} created={}>".format(self.owner.username, self.created)

    def get_absolute_url(self):
        return '/edit/{}'.format(self.pk)
