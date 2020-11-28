from martor.widgets import AdminMartorWidget

from django.contrib import admin
from django.db import models

from .models import HomeAlert


class HomeAlertAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': AdminMartorWidget},
    }


admin.site.register(HomeAlert, HomeAlertAdmin)
