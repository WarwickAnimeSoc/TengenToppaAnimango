from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


# Removed discord webhook integration from the model as it was never used and unneeded.
class Article(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(blank=True, editable=False)

    # Renamed "blog" category from aniMango to "other" as that's a more accurate description of the few articles that
    # will be posted there.
    ARTICLE_CHOICES = (
        ('news', 'News'),
        ('minutes', 'Minutes'),
        ('other', 'Other')
    )
    article_type = models.CharField(max_length=8, choices=ARTICLE_CHOICES, default='news')
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, null=False)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Article, self).save()
