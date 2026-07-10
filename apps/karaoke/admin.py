from django.db.models import QuerySet
from django.http import HttpRequest
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.utils.html import format_html

from .models import Song, Request, ArchivedRequest


class RequestAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'artist',
        'show_ultrastar_url',
    ]

    actions = [
        'complete',
        'cancel',
    ]

    search_fields = [
        'artist',
        'title',
    ]

    def show_ultrastar_url(self, obj: Request) -> str:
        return format_html("<a href='{url}' target=\"_blank\">{url}</a>", url=obj.ultrastar_url)

    @admin.action(description="Complete the request")
    def complete(self, request: HttpRequest, queryset: QuerySet[Request]) -> None:
        for request_obj in queryset:
            try:
                request_obj.complete()
            except ValidationError:
                messages.error(request, "{0} has an invalid AniList link".format(request_obj))

    @admin.action(description="Cancel the request")
    def cancel(self, request: HttpRequest, queryset: QuerySet[Request]) -> None:
        for request_obj in queryset:
            request_obj.remove()


class ArchivedRequestAdmin(admin.ModelAdmin):
    list_display = [
        'ultrastar_url',
        'status',
    ]


class SongAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'artist',
        'related_series',
    ]

    search_fields = [
        'artist',
        'title',
    ]

    raw_id_fields = ['related_series']


admin.site.register(Song, SongAdmin)
admin.site.register(Request, RequestAdmin)
admin.site.register(ArchivedRequest, ArchivedRequestAdmin)
