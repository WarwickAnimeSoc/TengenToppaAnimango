from martor.widgets import AdminMartorWidget
from datetime import timedelta

from django import forms
from django.db import models
from django.contrib import admin, messages
from django.contrib.admin.helpers import ActionForm

from .models import Event, Signup


class PropagateEventForm(ActionForm):
    propagate_weeks_number = forms.CharField(required=False)


class SignupInline(admin.StackedInline):
    model = Signup
    fields = ['member', 'comment', 'verified']
    readonly_fields = ['member', 'comment']
    extra = 0


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

    inlines = [SignupInline]

    list_display = (
        'title',
        'event_start_date',
        'event_end_date',
        'event_location',
        'signup_count'
    )

    action_form = PropagateEventForm
    actions = (
        'propagate_weekly',
    )

    def propagate_weekly(self, request, queryset):
        try:
            propagate_weeks_number = request.POST.get('propagate_weeks_number')
            if not propagate_weeks_number:
                raise ValueError
            propagate_weeks_number = int(propagate_weeks_number)
        except ValueError:
            self.message_user(request, 'Please enter an integer.', messages.ERROR)
            return

        # Propagates an event for a given number of weeks. All the event data will be the same, except for the dates
        # which will be incremented by 1 week.
        # This is intended to be used to quickly list weekly events (e.g. the main series)
        for event in queryset:
            for i in range(0, propagate_weeks_number):
                # Setting the primary key to none allows for cloning objects
                # https://docs.djangoproject.com/en/3.1/topics/db/queries/#copying-model-instances

                # The Event object referenced by the event variable will always update to "point" to the latest Event
                # so the timedelta need to be 1 week.
                event.pk = None
                event.event_start_date = event.event_start_date + timedelta(weeks=1)
                event.event_end_date = event.event_end_date + timedelta(weeks=1)

                # Increment signup times if needed
                if event.signups_open_date:
                    event.signups_open_date = event.signups_open_date + timedelta(weeks=1)
                if event.signups_close_date:
                    event.signups_close_date = event.signups_open_date + timedelta(weeks=1)

                event.save()

    propagate_weekly.short_description = "Create x amount copies of this event, each 1 week apart."


admin.site.register(Event, EventAdmin)
