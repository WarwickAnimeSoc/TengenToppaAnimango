from django.db import models
from django.template.defaultfilters import date as django_date
from django.utils import timezone, dateformat

from apps.members.models import Member


def nice_date(date, long=True):
    date_formatter = dateformat.DateFormat(date)
    if date.date() == timezone.now().date():
        return 'today'
    else:
        if long:
            return 'on {0!s} the {1!s} of {2!s}'.format(date_formatter.format('l'), date_formatter.format('jS'),
                                                        date_formatter.format('F Y'))
        else:
            return 'on the {0!s} of {1!s}'.format(date_formatter.format('jS'), date_formatter.format('F Y'))


def nice_time(date):
    date_formatter = dateformat.DateFormat(date)
    return date_formatter.format('H:i')


class Event(models.Model):
    title = models.CharField(max_length=150)
    subtitle = models.CharField(max_length=150, blank=True)
    details = models.TextField()
    event_start_date = models.DateTimeField()
    event_end_date = models.DateTimeField()
    event_location = models.CharField(max_length=100, blank=True)
    maximum_signups = models.IntegerField(help_text='Set to something < 1 if signing up is not required')
    signups_open_date = models.DateTimeField(blank=True, null=True)
    signups_close_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{0!s}, {1!s}, {2!s}'.format(self.title, django_date(self.event_start_date, 'D jS F Y, H:i'),
                                            self.event_location)

    def signup_required(self):
        return self.maximum_signups > 0

    def is_full(self):
        return self.signup_required() and self.signup_set.count() >= self.maximum_signups

    def already_signed_up(self, member):
        return self.signup_set.filter(member=member).exists()

    def signup_count(self):
        return str(self.signup_set.count()) + '/' + str(self.maximum_signups)

    def signups_open(self):
        # This method returns True if it is past the event signups open date. However, this does not mean that it will
        # be possible to sign up, as signups may have closed. To check if signups are possible, signups_closed() must
        # also be used.
        if not self.signups_open_date:
            return False

        return self.signups_open_date < timezone.now()

    def signups_closed(self):
        if not self.signups_close_date:
            return False

        return self.signups_close_date < timezone.now()

    def one_day_event(self):
        return self.event_start_date.date() == self.event_end_date.date()

    def nice_signups_date(self):
        # Used when displaying the event's details
        # Prefix in template: "Signups for this event will open "
        return '{0!s} at {1!s}'.format(nice_date(self.signups_open_date), nice_time(self.signups_open_date))

    def nice_when_descriptor(self):
        # Used when displaying the event's details
        # Prefix in template: "When: "
        if self.one_day_event():
            when_string = '{0!s} at {1!s}'.format(nice_date(self.event_start_date), nice_time(self.event_start_date))
        else:
            when_string = '{0!s} at {1!s} until {2!s} at {3!s}'.format(nice_date(self.event_start_date),
                                                                       nice_time(self.event_start_date),
                                                                       nice_date(self.event_end_date),
                                                                       nice_time(self.event_end_date))
        return when_string[0].upper() + when_string[1:]

    def nice_eta_descriptor(self):
        # Used when displaying the event on the events page
        # Prefix in template: None
        if self.event_start_date > timezone.now():
            return 'Starts {0!s} at {1!s}'.format(nice_date(self.event_start_date), nice_time(self.event_start_date))
        elif self.event_end_date < timezone.now():
            return 'Ended {0!s}'.format(nice_date(self.event_end_date, long=False))
        else:
            return 'Ends {0!s} at {1!s}'.format(nice_date(self.event_end_date), nice_time(self.event_end_date))

    class Meta:
        ordering = ['-event_start_date']


class Signup(models.Model):
    member = models.ForeignKey(Member, on_delete=models.PROTECT)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    comment = models.CharField(max_length=200, blank=True)
    created = models.DateTimeField()

    def __str__(self):
        return str(self.member) + ' signup for ' + str(self.event)
