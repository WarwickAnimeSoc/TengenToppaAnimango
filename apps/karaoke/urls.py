from django.urls import path

from . import views

app_name = 'karaoke'

urlpatterns = [
    path('list/<page>/', views.karaoke_list, name='karaoke_list'),
    path('requests/', views.request_song, name='request'),
    path('guide/', views.mapping_guide, name='guide'),
]
