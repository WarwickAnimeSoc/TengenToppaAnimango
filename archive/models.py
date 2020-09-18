import re

from django.db import models


class Item(models.Model):
    name = models.CharField(null=True, blank=True, max_length=40, help_text='Displayed name rather than filename.')

    # aniMango had 4 type choices for archive files: Images, Videos, Text files and Website files. Given that the
    # text files and website files types were not used and couldn't even be displayed on the site if they were (old
    # archive app could only show images and videos) they are not an option in this version of the site.
    TYPE_CHOICES = (
        ('im', 'Image'),
        ('vi', 'Video'),
    )
    type = models.CharField(max_length=2, choices=TYPE_CHOICES, default='im')
    date = models.DateField(null=False, help_text='Date of creation or last known time.')
    file = models.FileField(null=False, blank=False, upload_to='archive/', help_text='The file that should be uploaded')
    details = models.TextField(null=True, blank=True, help_text='Any details about the item')

    def __str__(self):
        if self.name:
            return '{0} | {1} | {2}'.format(self.get_type_display(), self.date, self.name)
        else:
            return '{0} | {1} | {2}'.format(self.get_type_display(), self.date, self.file.name)
