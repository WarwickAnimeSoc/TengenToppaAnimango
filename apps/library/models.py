import datetime

from django.db import models
from django.contrib.auth.models import User

from apps.showings.models import Series


class Item(models.Model):
    parent_series = models.ForeignKey(Series, on_delete=models.CASCADE)
    name = models.CharField(max_length=128, blank=False, null=False)
    MEDIA_TYPE_CHOICES = (
        ('Manga', 'Manga'),
        ('Light Novel', 'Light Novel'),
        ('DVD', 'DVD'),
        ('BD', 'BD'),
    )
    media_type = models.CharField(max_length=16, choices=MEDIA_TYPE_CHOICES, blank=False)
    details = models.CharField(max_length=64, blank=True)

    def __str__(self):
        return '{0!s} of {1!s}'.format(self.name, self.parent_series.nice_title())

    def status(self):
        if not Request.objects.filter(item=self).exists():
            return 'Available'
        return Request.objects.get(item=self).status()

    def request(self, user):
        # if request for this item already exists, then it's taken and cannot be requested
        if Request.objects.filter(item=self).exists():
            return None
        request = Request()
        request.item = self
        request.status_variable = 'Requested'
        request.user = user
        request.save()
        return request


class Request(models.Model):
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    date_requested = models.DateTimeField(auto_now_add=True)
    return_deadline = models.DateField(blank=True, null=True,
                                       help_text='Filled automatically on approval. Default loan period - 2 weeks. '
                                                 'Set manually to override.')
    STATUS_CHOICES = (
        ('Requested', 'Requested'),
        ('On Loan', 'On Loan'),
        ('Late', 'Late'),
    )
    # Use status_variable only for setting it. For getting use def self.status(), this ensures that that the status
    # variable is up to date when you display it.
    status_variable = models.CharField(max_length=16, choices=STATUS_CHOICES, blank=False, null=False)
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=False)

    def __str__(self):
        return '{0!s}: {1!s} ({2!s})'.format(self.status(), self.item.parent_series.nice_title(), self.item.name)

    def status(self):
        if self.return_deadline:
            if datetime.date.today() > self.return_deadline:
                self.status_variable = 'Late'
                self.save()
        return self.status_variable

    def approve(self):
        if self.status() == 'Requested':
            self.status_variable = 'On Loan'
            if not self.return_deadline:
                self.return_deadline = datetime.date.today() + datetime.timedelta(weeks=2)
            self.save()
            return True
        return False

    def deny(self):
        if self.status() == 'Requested':
            self.archive('Denied')
            self.delete()
            return True
        return False

    def absent(self):
        if self.status() == 'Requested':
            self.archive('Absent')
            self.delete()
            return True
        return False

    def returned(self, status):
        if 'Late' == status and not self.status() == 'Late':
            # Prevent user error when marking returned item as late when it is not late -Sorc
            return False
        if self.status() == 'On Loan' or self.status() == 'Late':
            self.archive(status)
            self.delete()
            return True
        return False

    def archive(self, status):
        request = ArchivedRequest()
        request.item = self.item
        request.date_requested = self.date_requested
        request.return_deadline = None if status == 'Denied' or status == 'Absent' else self.return_deadline
        request.date_finalised = datetime.date.today()
        request.status = status
        request.user = self.user
        request.save()

    def renew(self):
        if (self.status_variable == 'On Loan' or self.status_variable == 'Late') and self.return_deadline:
            self.return_deadline += datetime.timedelta(weeks=1)
            self.status_variable = 'On Loan'
            self.save()
            return True
        return False

    class Meta:
        ordering = ['-date_requested']


class ArchivedRequest(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    date_requested = models.DateTimeField()
    date_finalised = models.DateField()
    return_deadline = models.DateField(null=True)
    STATUS_CHOICES = (
        ('Denied', 'Denied'),
        ('Late', 'Late'),
        ('Returned', 'Returned'),
        ('Absent', 'Absent'),
    )
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, blank=False, null=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
