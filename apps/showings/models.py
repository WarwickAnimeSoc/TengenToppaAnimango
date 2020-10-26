from datetime import date, timedelta

from django.db import models
from django.core.exceptions import ValidationError

from .anilist_api import populate_series_item


# Series model which describes an Anime or Manga has been moved to the showings app from the library app
# Removed the wiki_link field from the model as it's not very useful. MAL and Anilist are more than enough.
class Series(models.Model):
    auto_populate_data = models.BooleanField(default=False, help_text='Check this to use AniList to populate fields.')
    title_romaji = models.CharField(max_length=110, blank=True)
    title_english = models.CharField(max_length=110, blank=True)
    api_id = models.IntegerField(unique=True, null=True, blank=True)
    series_type = models.CharField(max_length=10, blank=True)
    synopsis = models.TextField(blank=True)
    cover_link = models.URLField(blank=True)
    anilist_link = models.URLField(blank=True)
    mal_link = models.URLField(blank=True)

    # Cooldown for the series model is currently based on the cooldown rules laid out by the 2020/2021 exec team.
    # These rules are explained in the comments of the Show class.
    # Basically though, some shows could be on cooldown for exec choice, which means they can't be exec choices, but not
    # on cooldown for main series, so to display this properly on the website, we need to store they type of showing
    # which triggered cooldown for this Series.
    # Cooldown also works by academic year, not calendar year which means the date stored in cooldown_end_date is
    # not actually when the item goes off cooldown.
    cooldown_end_date = models.DateField(null=True, blank=True, editable=False)
    last_shown_instance = models.ForeignKey('showings.Show', null=True, blank=True, on_delete=models.PROTECT,
                                            related_name='last_showing', editable=False)

    def cooldown_academic_year(self):
        if self.cooldown_end_date.month < 8:
            # Academic year ends on year stored
            return '{0!s}/{1!s}'.format(str(self.cooldown_end_date.year - 1), str(self.cooldown_end_date.year))
        else:
            # Academic year starts on year stored
            return '{0!s}/{1!s}'.format(str(self.cooldown_end_date.year), str(self.cooldown_end_date.year + 1))

    def is_on_cooldown(self):
        # This method only checks if a series is on cooldown, not what type of cooldown it's on. This is explained
        # further in the Show class.
        if 'anime' == self.series_type and self.cooldown_end_date:
            # Only anime can go on cooldown
            return self.cooldown_end_date > date.today()
        return False

    def nice_title(self):
        # Should display both the english and romaji title if possible.
        if self.title_english and self.title_romaji:
            return '{0!s} / {1!s}'.format(self.title_romaji, self.title_english)
        elif self.title_romaji:
            return '{0!s}'.format(self.title_romaji)
        elif self.title_english:
            # This case should never really occur, as most times data will be populated from anilist, where all shows
            # have a romaji title.
            return '{0!s}'.format(self.title_english)
        else:
            return 'ERROR TITLE NOT SET'

    def __str__(self):
        # Should display both the english and romaji title when available. It's assumed that both the romaji title and
        # series type will always be available (which they will be if AniList is used to populate the fields).
        if self.series_type:
            return '{0!s}: {1!s}'.format(self.series_type, self.nice_title())
        else:
            return 'Unknown series'

    class Meta:
        verbose_name_plural = 'series'

    def save(self, *args, **kwargs):
        # Save method is overwritten to use the anilist API to fill fields
        if self.auto_populate_data:
            # Setting auto_populate_date to false ensures that it won't be auto-populated every time it's saved
            self.auto_populate_data = False
            try:
                populate_series_item(self)
            except ValidationError:
                raise ValidationError('There was an error getting the data from Anilist, check the link is valid',
                                      'anilist_api_error')

        super(Series, self).save()


# A Showing is an event at which anime is shown at the society. A Showing consists of Shows, which represent an item
# which was shown at the society.
class Showing(models.Model):
    date = models.DateField()

    # Cooldown is not affected by this. That is handled within the Show class.
    SHOWING_CHOICES = (
        ('wk', 'Weekly showing'),
        ('an', 'All-nighter'),
        ('mo', 'Movie Night'),
        ('ot', 'Other')
    )
    showing_type = models.CharField(max_length=2, choices=SHOWING_CHOICES, blank=False, null=False, default='wk')

    # Replaced showing details (from aniMango) with showing title as it makes more sense. This should probably
    # only be set for special showings, like Holiday events events with a showing_type of other.
    showing_title = models.CharField(max_length=50, blank=True, null=True,
                                     help_text='You only need to set this if the event has a unique name.')

    def __str__(self):
        return '{0!s} - {1!s}'.format(self.get_showing_type_display(), self.date.strftime('%a %d %b %Y'))

    class Meta:
        ordering = ['-date']


# A Show is an item that was shown at the society, this is different from a Series.
class Show(models.Model):
    series = models.ForeignKey(Series, null=False, on_delete=models.PROTECT)
    details = models.CharField(max_length=200, help_text='Episodes watched (Ep.1, Eps. 1-3), ect.')
    shown_at = models.ForeignKey(Showing, null=False, blank=False, on_delete=models.CASCADE)

    # This choice will affect the cooldown of the Series in question.
    TYPE_CHOICES = (
        ('ms', 'Main series'),
        ('mc', 'Main series candidate'),
        ('ex', 'Exec choice'),
        ('mv', 'Movie Night'),
        ('an', 'All-nighter'),
        ('ot', 'Other'),
    )
    show_type = models.CharField(max_length=2, choices=TYPE_CHOICES, null=False, blank=False)

    def __str__(self):
        return '{0!s} - {1!s}'.format(self.series.nice_title(), self.shown_at)

    def apply_cooldown(self):
        # Cooldown is applied to the Series object linked to this Show object in this method.
        # The cooldown rules that are followed here are the ones set by the 2020/2021 exec.
        # These rules are laid out in the flowchart found in './static/images/cooldown_flowchart_2020-2021.png'
        # They are also written out below:
        #
        # For Main series:
        #   An unsuccessful main series candidate is placed on cooldown until the next academic year
        #   A successful main series candidate (in other words a main series) is placed on cooldown for 3 academic years
        # For Exec choices:
        #   An unsuccessful exec choice candidate is not placed on cooldown
        #   A successful exec choice candidate is placed on EXEC CHOICE COOLDOWN for two academic years, this means
        #   that it can be a main series but not an exec choice.
        # For Move Nights:
        #   A movie is placed on cooldown for two academic years.
        # Other events:
        #   No cooldown rules
        #
        # Cooldown will always overwrite the previous cooldown, even if it's not over. Although if that happened, it
        # would mean something was show whilst on cooldown.
        # As timedelta does not support academic years, cooldown is internally handled by calendar year, when displaying
        # on the website, calendar years need to be converted to academic years.
        if self.show_type == 'mc':
            # Place on cooldown for 1 academic year
            self.series.last_shown_instance = self
            self.series.cooldown_end_date = self.shown_at.date + timedelta(days=365)
        elif self.show_type == 'ms':
            # Place on cooldown for 3 academic years.
            # As cooldown is overwritten each showing, the cooldown_end_date for a main series will be 3 years after
            # the last episode was shown. This shouldn't affect anything though as the site should display cooldown by
            # academic year.
            self.series.last_shown_instance = self
            self.series.cooldown_end_date = self.shown_at.date + timedelta(days=1095)
        elif self.show_type == 'ex':
            # Place on cooldown for 2 academic years.
            # Remember that this cooldown only applies to having this show as an exec choice again, it could still
            # be a main series so the site needs to reflect this when displaying cooldown info.
            self.series.last_shown_instance = self
            self.series.cooldown_end_date = self.shown_at.date + timedelta(days=730)
        elif self.show_type == 'mv':
            # Place on cooldown for 2 academic years.
            # This code is identical to the one for exec choices, but it's separated so that it's easier to change
            # should the cooldown rules be changed.
            self.series.last_shown_instance = self
            self.series.cooldown_end_date = self.shown_at.date + timedelta(days=730)
        else:
            # No cooldown
            pass
        self.series.save()

    def save(self, *args, **kwargs):
        # Overwrite save to apply cooldown
        # The super save is called twice, this was needed when importing the old showings from aniMango, as the related
        # Series object won't save if the Show is unsaved.
        super(Show, self).save()
        self.apply_cooldown()
        super(Show, self).save()
