from django.contrib import admin
from .models import Product, Alert

admin.site.register(Product)
admin.site.register(Alert)
from .models import NotebookEntry

admin.site.register(NotebookEntry)
