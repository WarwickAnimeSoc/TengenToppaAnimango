import bleach

from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from .models import Request, Song


class KaraokeRequestForm(forms.Form):
    ultrastar_validator = RegexValidator(r'^https:\/\/ultrastar-es\.org\/en\/canciones\?.*$', message="Invalid url")
    anilist_validator = RegexValidator(r'^https:\/\/anilist\.co\/anime\/[0-9]*\/?.*$', message="Invalid url")

    title = forms.CharField(label="Song title", max_length=200)
    artist = forms.CharField(label="Song artist", max_length=200)
    ultrastar_url = forms.URLField(label="Ultrastar url", validators=[ultrastar_validator])
    anilist_url = forms.URLField(label="Anilist url", validators=[anilist_validator], required=False)

    # Clean HTML from title and artist fields
    def clean_title(self):
        title = self.cleaned_data['title']
        return bleach.clean(title, tags=[], attributes={}, styles=[], strip=True)

    def clean_artist(self):
        artist = self.cleaned_data['artist']
        return bleach.clean(artist, tags=[], attributes={}, styles=[], strip=True)

    def clean(self):
        cleaned_data = super(KaraokeRequestForm, self).clean()

        # For the form to be valid we need to check that the song has not already been requested or does not
        # already exist in the database. There is a rare case where two different songs might have the exact same name
        # and artist, but this is pretty rare so it should be handled on a case by case basis.
        request = Request.objects.filter(artist=cleaned_data.get('artist', None),
                                         title=cleaned_data.get('title', None)).distinct()
        if request:
            raise ValidationError('This song appears to have already been requested')

        song = Song.objects.filter(artist=cleaned_data.get('artist', None),
                                   title=cleaned_data.get('title', None)).distinct()
        if song:
            raise ValidationError('This song appears to already be in the list')

        return cleaned_data

    def submit(self, member):
        request = Request()
        request.title = self.cleaned_data['title']
        request.artist = self.cleaned_data['artist']
        request.ultrastar_url = self.cleaned_data['ultrastar_url']
        request.anilist_url = self.cleaned_data['anilist_url']
        request.requester = member
        request.save()
