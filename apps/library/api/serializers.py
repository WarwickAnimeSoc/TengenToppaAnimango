from rest_framework import serializers

from apps.showings.models import Series


class LibrarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Series
        fields = [
            'id',
            'title_romaji',
            'title_english',
            'api_id',
            'series_type',
            'synopsis',
            'cover_link',
            'anilist_link',
            'mal_link'
        ]
