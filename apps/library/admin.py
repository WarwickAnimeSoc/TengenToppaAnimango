from django.db.models import QuerySet
from django.http import HttpRequest
from django import forms
from django.contrib import admin, messages
from django.contrib.admin.helpers import ActionForm
from django.contrib.auth.models import User

from .models import Item, Request, ArchivedRequest


class CreateLoanForm(ActionForm):
    university_id = forms.CharField(required=False)


class ItemAdmin(admin.ModelAdmin):
    raw_id_fields = ['parent_series']

    list_display = [
        '__str__',
        'media_type',
        'parent_series',
        'status',
    ]

    list_filter = ['media_type']

    search_fields = [
        'parent_series__title_english',
        'parent_series__title_romaji',
    ]

    action_form = CreateLoanForm
    actions = ['manual_request']

    @admin.action(description="Issue loan to user manually")
    def manual_request(self, request: HttpRequest, queryset: QuerySet[Item]) -> None:
        university_id = request.POST.get('university_id')
        if not university_id:
            self.message_user(request, 'Please provide the university ID.', messages.ERROR)
        else:
            try:
                user = User.objects.get(username=university_id)
                for item in queryset:
                    request_obj = item.request(user)
                    if request_obj:
                        request_obj.approve()
                        msg_string = 'Successfully issued loan for {0!s}.'.format(item)
                        self.message_user(request, msg_string, messages.SUCCESS)
                    else:
                        msg_string = 'Could not issue loan for {0!s}.'.format(item)
                        self.message_user(request, msg_string, messages.ERROR)
            except User.DoesNotExist:
                self.message_user(request, 'User {0!s} could not be found.'.format(university_id), messages.ERROR)


class RequestAdmin(admin.ModelAdmin):
    readonly_fields = [
        'item',
        'date_requested',
        'status_variable',
        'user',
    ]

    list_display = [
        'item',
        'status_variable',
        'return_deadline',
        'user',
    ]

    list_filter = ['status_variable']

    search_fields = ['item']

    actions = [
        'approve',
        'deny',
        'absent',
        'return_on_time',
        'return_late',
        'renew',
    ]

    @admin.action(description="Approve loan request for selected item")
    def approve(self, request: HttpRequest, queryset: QuerySet[Request]) -> None:
        for request_obj in queryset:
            if request_obj.approve():
                msg_string = 'Successfully approved loan for {0!s}.'.format(request_obj.item)
                self.message_user(request, msg_string, messages.SUCCESS)
            else:
                msg_string = 'Could not approve loan for {0!s}.'.format(request_obj.item)
                self.message_user(request, msg_string, messages.ERROR)

    @admin.action(description="Deny loan request for selected items")
    def deny(self, request: HttpRequest, queryset: QuerySet[Request]) -> None:
        for request_obj in queryset:
            if request_obj.deny():
                msg_string = 'Successfully denied loan for {0!s}.'.format(request_obj.item)
                self.message_user(request, msg_string, messages.SUCCESS)
            else:
                msg_string = 'Could not deny loan for {0!}s'.format(request_obj.item)
                self.message_user(request, msg_string, messages.ERROR)

    @admin.action(description="Mark item as not taken due to user being absent")
    def absent(self, request: HttpRequest, queryset: QuerySet[Request]) -> None:
        for request_obj in queryset:
            if request_obj.absent():
                msg_string = 'Successfully marked {0!s} as available.'.format(request_obj.item)
                self.message_user(request, msg_string, messages.SUCCESS)
            else:
                msg_string = 'Could not mark {0!s} as available.'.format(request_obj.item)
                self.message_user(request, msg_string, messages.ERROR)

    @admin.action(description="Mark items as returned on time")
    def return_on_time(self, request: HttpRequest, queryset: QuerySet[Request]) -> None:
        for request_obj in queryset:
            if request_obj.returned('Returned'):
                msg_string = 'Successfully marked {0!s} as returned.'.format(request_obj.item)
                self.message_user(request, msg_string, messages.SUCCESS)
            else:
                msg_string = 'Could not mark {0!s} as returned.'.format(request_obj.item)
                self.message_user(request, msg_string, messages.ERROR)

    @admin.action(description="Mark items as returned late")
    def return_late(self, request: HttpRequest, queryset: QuerySet[Request]) -> None:
        for request_obj in queryset:
            if request_obj.returned('Late'):
                msg_string = 'Successfully marked {0!s} as returned late.'.format(
                    request_obj.item)
                self.message_user(request, msg_string, messages.SUCCESS)
            else:
                msg_string = 'Could not mark {0!s} as returned late.'.format(request_obj.item)
                self.message_user(request, msg_string, messages.ERROR)

    @admin.action(description="Renew the selected items for one week")
    def renew(self, request: HttpRequest, queryset: QuerySet[Request]) -> None:
        for request_obj in queryset:
            if request_obj.renew():
                msg_string = 'Successfully renewed {0!s}.'.format(request_obj.item)
                self.message_user(request, msg_string, messages.SUCCESS)
            else:
                msg_string = 'Could not renew {0!s}.'.format(request_obj.item)
                self.message_user(request, msg_string, messages.ERROR)


class ArchivedRequestAdmin(admin.ModelAdmin):
    readonly_fields = [
        'item',
        'date_requested',
        'date_finalised',
        'return_deadline',
        'status',
        'user',
    ]

    list_display = [
        'item',
        'status',
        'date_requested',
        'date_finalised',
        'user',
    ]

    list_filter = ['status']

    search_fields = ['item']


admin.site.register(Item, ItemAdmin)
admin.site.register(Request, RequestAdmin)
admin.site.register(ArchivedRequest, ArchivedRequestAdmin)
