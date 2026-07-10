from django.urls import path

from . import views

app_name = 'news'

urlpatterns = [
    path('<category>/<int:page>/', views.news_listing, name='listing'),
    path('article/<int:article_id>/<article_slug>', views.article_detail, name='article_detail'),
]
