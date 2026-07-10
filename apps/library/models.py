from typing import Literal
import datetime

from django.db import models
from django.contrib.auth.models import User

from apps.showings.models import Series


class Item(models.Model):
    parent_series = models.ForeignKey(Series, on_delete=models.CASCADE)
    name = models.CharField(max_length=128, blank=False, null=False)

    class MediaType(models.TextChoices):
        MANGA = 'Manga', 'Manga'
        LIGHT_NOVEL = 'Light Novel', 'Light Novel'
        DVD = 'DVD', 'DVD'
        BD = 'BD', 'BD'

    media_type = models.CharField(max_length=16, choices=MediaType, blank=False)
    details = models.CharField(max_length=64, blank=True)

    def __str__(self) -> str:
        return '{0!s} of {1!s}'.format(self.name, self.parent_series.nice_title())

    def status(self) -> str:
        if not Request.objects.filter(item=self).exists():
            return 'Available'
        return Request.objects.get(item=self).status()

    def request(self, user: User) -> "Request | None":
        # if request for this item already exists, then it's taken and cannot be requested
        if Request.objects.filter(item=self).exists():
            return None
        request = Request()
        request.item = self
        request.status_variable = Request.Status.REQUESTED
        request.user = user
        request.save()
        return request


class Request(models.Model):
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    date_requested = models.DateTimeField(auto_now_add=True)
    return_deadline = models.DateField(blank=True, null=True,
                                       help_text='Filled automatically on approval. Default loan period - 2 weeks. '
                                                 'Set manually to override.')

    class Status(models.TextChoices):
        REQUESTED = 'Requested', 'Requested'
        ON_LOAN = 'On Loan', 'On Loan'
        LATE = 'Late', 'Late'

    # Use status_variable only for setting it. For getting use def self.status(), this ensures that that the status
    # variable is up to date when you display it.
    status_variable = models.CharField(max_length=16, choices=Status, blank=False, null=False)
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=False)

    def __str__(self) -> str:
        return '{0!s}: {1!s} ({2!s})'.format(self.status(), self.item.parent_series.nice_title(), self.item.name)

    def status(self) -> Status:
        if self.return_deadline:
            if datetime.date.today() > self.return_deadline:
                self.status_variable = Request.Status.LATE
                self.save()
        return self.status_variable

    def approve(self):
        if self.status() == Request.Status.REQUESTED:
            self.status_variable = Request.Status.ON_LOAN
            if not self.return_deadline:
                self.return_deadline = datetime.date.today() + datetime.timedelta(weeks=2)
            self.save()
            return True
        return False

    def deny(self):
        if self.status() == Request.Status.REQUESTED:
            self.archive(ArchivedRequest.Status.DENIED)
            self.delete()
            return True
        return False

    def absent(self):
        if self.status() == Request.Status.REQUESTED:
            self.archive(ArchivedRequest.Status.ABSENT)
            self.delete()
            return True
        return False

    def returned(self, status: "ArchivedRequest.Status"):
        if ArchivedRequest.Status.LATE == status and not self.status() == Request.Status.LATE:
            # Prevent user error when marking returned item as late when it is not late -Sorc
            return False
        if self.status() == Request.Status.ON_LOAN or self.status() == Request.Status.LATE:
            self.archive(status)
            self.delete()
            return True
        return False

    def archive(self, status: "ArchivedRequest.Status"):
        request = ArchivedRequest()
        request.item = self.item
        request.date_requested = self.date_requested
        if status == ArchivedRequest.Status.DENIED or status == ArchivedRequest.Status.ABSENT:
            request.return_deadline = None
        else:
            request.return_deadline = self.return_deadline
        request.date_finalised = datetime.date.today()
        request.status = status
        request.user = self.user
        request.save()

    def renew(self):
        if (self.status_variable == Request.Status.ON_LOAN or self.status_variable == Request.Status.LATE) and self.return_deadline:
            self.return_deadline += datetime.timedelta(weeks=1)
            self.status_variable = Request.Status.ON_LOAN
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

    class Status(models.TextChoices):
        DENIED = 'Denied', 'Denied'
        LATE = 'Late', 'Late'
        RETURNED = 'Returned', 'Returned'
        ABSENT = 'Absent', 'Absent'

    status = models.CharField(max_length=16, choices=Status, blank=False, null=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
