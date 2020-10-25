from rest_framework import generics, filters

from apps.events.models import Event
from .serializers import EventSerializer


class EventsListView(generics.ListAPIView):
    serializer_class = EventSerializer
    queryset = Event.objects.all()
    filter_backends = (filters.OrderingFilter,)
    ordering_field = 'event_start_date'
