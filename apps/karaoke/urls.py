from django.urls import path

from . import views

app_name = 'karaoke'

urlpatterns = [
    path('list/<page>/', views.karaoke_list, name='karaoke_list'),
    path('requests/', views.request_song, name='request'),
    path('guide/', views.mapping_guide3, name='guide'),
    path('guide3/', views.mapping_guide3, name='guide3'),
    path('guide2/', views.mapping_guide2, name='guide2'),
]
