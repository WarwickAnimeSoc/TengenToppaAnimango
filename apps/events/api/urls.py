from django.urls import re_path
from .views import EventsListView

urlpatterns = [
    re_path(r'^$', EventsListView.as_view(), name='events_api_list'),
]

