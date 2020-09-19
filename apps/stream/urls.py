from django.urls import path

from . import views

app_name = 'stream'

urlpatterns = [
    path('', views.stream, name='stream'),
    path('viewcount/', views.viewcount, name='viewcount'),
    path('viewtick', views.viewtick, name='viewtick')
]
