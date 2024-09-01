from django.urls import path

from . import views

app_name = 'miscellaneous'

urlpatterns = [
    path('home', views.home, name='home'), #remember to change this to default site ''
    path('privacy/', views.privacy, name='privacy'),
    path('discord', views.discord, name='discord'),
    path('instagram', views.instagram, name='instagram'),
    path('warwicksu', views.warwicksu, name='warwicksu'),
    path('malclub', views.malclub, name='malclub'),
    path('github', views.github, name='github'),
    path('klist', views.karaoke_list, name='karaoke_list'),
    path('', views.welcomeweek, name='welcomeweek2024'), #get rid of this and below after ww
    path('welcomeweek2024', views.welcomeweek, name='welcomeweek2024')
]

