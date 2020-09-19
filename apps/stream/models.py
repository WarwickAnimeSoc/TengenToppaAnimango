from datetime import timedelta

from django.db import models
from django.utils import timezone


class ViewCounter(models.Model):
    name = models.CharField(max_length=20)

    def prune(self):
        cutoff_time = timezone.now() - timedelta(minutes=1)
        views_to_delete = self.view_set.filter(last_updated__lt=cutoff_time)
        for view in views_to_delete:
            view.delete()

    def count(self):
        return str(self.view_set.count())

    def __str__(self):
        return self.name


class View(models.Model):
    related_counter = models.ForeignKey(ViewCounter, on_delete=models.CASCADE)
    token = models.CharField(max_length=20)
    last_updated = models.DateTimeField()
