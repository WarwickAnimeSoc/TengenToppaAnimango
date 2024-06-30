from django.urls import path
from . import views

app_name = 'anisoc_awards'

urlpatterns = [
    path('', views.anisoc_awards, name='anisoc_awards'),
]