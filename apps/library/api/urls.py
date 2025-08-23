from django.urls import re_path

from .views import LibraryListView


urlpatterns = [
    re_path(r'^$', LibraryListView.as_view(), name='library_list_api'),
]