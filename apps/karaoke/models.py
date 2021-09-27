import re

from django.db import models

from apps.showings.models import Series


class Song(models.Model):
    title = models.CharField(max_length=200, blank=False)
    artist = models.CharField(max_length=200, blank=False)
    related_series = models.ForeignKey(Series, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return '{0!s} - {1!s}'.format(self.artist, self.title)

    class Meta:
        unique_together = ('title', 'artist')


class Request(models.Model):
    title = models.CharField(max_length=200, blank=False)
    artist = models.CharField(max_length=200, blank=False)
    anilist_url = models.URLField(blank=True)
    ultrastar_url = models.URLField(blank=False, unique=True)

    def __str__(self):
        return '{0!s} - {1!s}'.format(self.artist, self.title)

    def complete(self):
        song = Song()
        # The song/request title and artist fields are user submitted. However, they should be validated by the
        # submission form and any unwanted text (such as html) removed at that point.
        song.title = self.title
        song.artist = self.artist
        # If the user has provided an anilist url for the show, we can try to automatically create a related Series
        # for the song.
        if self.anilist_url:
            # The request form for Series should already have validated that the anilist_url field matches the correct
            # format for an anilist link. The link could still be invalid, but the format must be correct.
            url_values = re.split(r'/', re.sub(r'(https://)*(www\.)*(anilist.co/)*', '', str(self.anilist_url)))
            api_id = url_values[1]
            try:
                related_series = Series.objects.get(api_id=api_id)
            except Series.DoesNotExist:
                # Attempt to create a new series and auto populate the data using the link provided.
                # This can raise a ValidationError if the anilist url is invalid.
                new_series = Series(anilist_link=self.anilist_url, auto_populate_data=True)
                new_series.save()
                related_series = new_series

            song.related_series = related_series

        song.save()
        self.archive('completed', song)

    def remove(self):
        self.archive('cancelled')

    def archive(self, status, song=None):
        request = ArchivedRequest()
        request.ultrastar_url = self.ultrastar_url
        request.status = status
        if song is not None:
            request.related_song = song
        request.save()
        self.delete()


class ArchivedRequest(models.Model):
    related_song = models.ForeignKey(Song, null=True, blank=True, on_delete=models.CASCADE)
    ultrastar_url = models.URLField(blank=False)

    STATUS_CHOICES = (
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    )

    status = models.CharField(max_length=16, choices=STATUS_CHOICES, blank=False)

    def __str__(self):
        return '{0!s} - {1!s}'.format(self.ultrastar_url, self.status)