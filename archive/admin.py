from martor.widgets import AdminMartorWidget

from django.db import models
from django.contrib import admin

from .models import Item


class ItemAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': AdminMartorWidget},
    }


admin.site.register(Item, ItemAdmin)
