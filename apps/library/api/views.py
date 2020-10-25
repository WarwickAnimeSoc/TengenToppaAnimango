from rest_framework import generics, filters

from apps.showings.models import Series
from .serializers import LibrarySerializer


class LibraryListView(generics.ListAPIView):
    serializer_class = LibrarySerializer
    queryset = Series.objects.filter(item__isnull=False).distinct()
    filter_backends = (filters.SearchFilter,)
    search_fields = ('title_romaji', 'title_english',)
