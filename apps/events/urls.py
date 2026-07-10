from django.urls import path

from . import views

app_name = 'events'

urlpatterns = [
    path('<int:page>/', views.upcoming_events, name='upcoming'),
    path('previous/<int:page>/', views.previous_events, name='previous'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
    path('event/<int:event_id>/cancel/', views.cancel_signup, name="cancel_signup")
]
