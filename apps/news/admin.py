from martor.widgets import AdminMartorWidget

from django.db import models
from django.contrib import admin
from django.utils import timezone

from .models import Article


class ArticleAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': AdminMartorWidget},
    }

    readonly_fields = ['created', 'created_by']
    list_display = ['title', 'created', 'created_by', 'article_type']
    list_filter = ['article_type']

    def save_model(self, request, obj, form, change):
        # On aniMango only the creator of an article or the president/webmaster could edit articles. However,
        # I've decided to remove this as we had a case where the secretary wanted to edit an article they had written
        # but had been uploaded to the site by the webmaster. To prevent articles from being tampered with (although
        # no exec should do that anyway) restrict the news admin view to only president, webmaster and secretary roles.
        obj.created_by = request.user
        super(ArticleAdmin, self).save_model(request, obj, form, change)


admin.site.register(Article, ArticleAdmin)
