from martor.widgets import AdminMartorWidget

from django.db import models
from django.contrib import admin

from .models import AcademicYearEntry, ExecEntry


class ExecEntryInline(admin.StackedInline):
    model = ExecEntry
    extra = 6


class AcademicYearEntryAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': AdminMartorWidget},
    }

    inlines = [ExecEntryInline]


# The ExecEntry model is not registered as it complicates the admin view.
admin.site.register(AcademicYearEntry, AcademicYearEntryAdmin)
