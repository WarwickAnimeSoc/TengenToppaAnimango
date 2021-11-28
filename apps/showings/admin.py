from django.contrib import admin
from django import forms
from django.core.validators import RegexValidator

from .models import Series, Showing, Show


class SeriesForm(forms.ModelForm):
    anilist_link_validator = RegexValidator(r'^https:\/\/anilist\.co\/anime\/[0-9]*\/?.*$',
                                            message='Invalid anilist link.')
    anilist_link = forms.URLField(label='Anilist link', validators=[anilist_link_validator], required=False)


class SeriesAdmin(admin.ModelAdmin):
    actions = None
    form = SeriesForm
    search_fields = ['title_romaji', 'title_english']
    list_display = ['title_romaji', 'series_type', 'api_id']
    list_filter = ['series_type']


class ShowInline(admin.StackedInline):
    model = Show
    extra = 2
    raw_id_fields = ['series']


class ShowingAdmin(admin.ModelAdmin):
    inlines = [ShowInline]
    list_filter = ['showing_type']


# The Show model is not registered as it complicates things in the admin view.
admin.site.register(Series, SeriesAdmin)
admin.site.register(Showing, ShowingAdmin)
