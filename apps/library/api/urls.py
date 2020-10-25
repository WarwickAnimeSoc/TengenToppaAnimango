from django.urls import path

from .views import LibraryListView


urlpatterns = [
    path('', LibraryListView.as_view(), name='library_list_api'),
]