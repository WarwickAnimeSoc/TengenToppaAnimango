from martor.widgets import AdminMartorWidget

from django import forms
from django.db import models
from django.contrib import admin

from .models import Event, Signup


class EventForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super(EventForm, self).clean()

        event_start_date = cleaned_data['event_start_date']
        event_end_date = cleaned_data['event_end_date']
        signups_open_date = cleaned_data['signups_open_date']
        signups_close_date = cleaned_data['signups_close_date']
        maximum_signups = cleaned_data['maximum_signups']

        if maximum_signups > 0:
            if not signups_open_date or not signups_close_date:
                raise forms.ValidationError('Please enter dates for the signup window')

            if event_start_date < signups_open_date:
                raise forms.ValidationError('Signups must open before the event starts')

            if signups_open_date > signups_close_date:
                raise forms.ValidationError('Signups must open before they close')

        if event_start_date > event_end_date:
            raise forms.ValidationError('The event must end after it starts')

    class Meta:
        model = Event
        fields = '__all__'


class EventAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': AdminMartorWidget},
    }

    form = EventForm

    list_display = (
        'title',
        'event_start_date',
        'event_end_date',
        'event_location',
        'signup_count'
    )


admin.site.register(Event, EventAdmin)