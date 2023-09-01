from django.urls import path

from . import views

app_name = 'miscellaneous'

urlpatterns = [
    path('', views.home, name='home'),
    path('privacy/', views.privacy, name='privacy'),
    path('discord', views.discord, name='discord'),
    path('facebook', views.facebook, name='facebook'),
    path('warwicksu', views.warwicksu, name='warwicksu'),
    path('malclub', views.malclub, name='malclub'),
    path('github', views.github, name='github'),
    path('klist', views.karaoke_list, name='karaoke_list'),
    path('welcomeweek2023',views.welcomeweek, name='welcomeweek2023')
]

