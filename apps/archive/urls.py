from django.urls import path

from . import views

app_name = 'archive'

urlpatterns = [
    path('', views.index, name='index'),
    path('<year>/', views.year_view, name='year'),
    path('item/<item_id>/', views.item_view, name='item'),
]
