from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, InvalidPage

from .models import Article


def news_listing(request, category, page):
    if category == 'all':
        articles = Article.objects.order_by('-created')
    else:
        articles = Article.objects.filter(article_type=category).order_by('-created')

    if not request.user.is_authenticated:
        articles = articles.filter(members_only=False)

    paginator = Paginator(articles, 12)
    try:
        context_articles_page = paginator.page(page)
    except InvalidPage:
        context_articles_page = paginator.page(1)

    return render(request, 'news/list.html', context={'category': category, 'articles_page': context_articles_page})


def article_detail(request, article_id, article_slug):
    article = get_object_or_404(Article, id=article_id)
    if article.members_only and not request.user.is_authenticated:
        return redirect('members:login_view')

    return render(request, 'news/article_detail.html', context={'article': article})
