from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


# Removed discord webhook integration from the model as it was never used and unneeded.
class Article(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(blank=True, editable=False, max_length=200)
    members_only = models.BooleanField(default=False)

    # Renamed "blog" category from aniMango to "other" as that's a more accurate description of the few articles that
    # will be posted there.
    class Type(models.TextChoices):
        NEWS = 'news', 'News'
        MINUTES = 'minutes', 'Minutes'
        OTHER = 'other', 'Other'

    article_type = models.CharField(max_length=8, choices=Type, default=Type.NEWS)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, null=False)

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs) -> None:
        self.slug = slugify(self.title)
        super(Article, self).save()
