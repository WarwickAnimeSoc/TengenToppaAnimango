from django.urls import path

from . import views

app_name = 'site_info'

urlpatterns = [
    path('', views.home, name='home'),
    path('discord', views.discord, name='discord'),
    path('facebook', views.facebook, name='facebook'),
    path('warwicksu', views.warwicksu, name='waricksu'),
    path('malclub', views.malclub, name='malclub')
]

