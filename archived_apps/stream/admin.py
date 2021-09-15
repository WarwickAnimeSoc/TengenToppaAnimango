from django.contrib import admin

from .models import ViewCounter


class ViewCounterAdmin(admin.ModelAdmin):
    pass


admin.site.register(ViewCounter, ViewCounterAdmin)
