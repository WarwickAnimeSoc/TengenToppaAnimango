from rest_framework import serializers
from apps.events.models import Event


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            'id',
            'title',
            'subtitle',
            'event_start_date',
            'event_end_date',
            'event_location',
            'details',
            'maximum_signups',
            'signups_open_date',
            'signups_close_date',
        ]
