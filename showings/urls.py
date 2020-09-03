from django.urls import path

from . import views

app_name = 'showings'

urlpatterns = [
    path('<page>/', views.showings, name='showings'),
    path('cooldown', views.cooldown_dashboard, name='cooldown_dashboard'),
]

