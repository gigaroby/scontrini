from django.contrib import admin
from .models import Receipt


class ReceiptAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'completed', 'category']
admin.site.register(Receipt, ReceiptAdmin)
