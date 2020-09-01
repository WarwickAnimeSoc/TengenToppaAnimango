from django.urls import path

from . import views

app_name = 'events'

urlpatterns = [
    path('<page>/', views.upcoming_events, name='upcoming'),
    path('previous/<page>/', views.previous_events, name='previous'),
    path('event/<event_id>/', views.event_detail, name='event_detail'),
    path('event/<event_id>/cancel/', views.cancel_signup, name="cancel_signup")
]

