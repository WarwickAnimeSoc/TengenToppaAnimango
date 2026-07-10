from django.urls import path

from . import views

app_name = 'library'

urlpatterns = [
    path('<int:page>/', views.library_list, name='library_list'),
    path('details/<int:series_id>/', views.series_view, name='series_view'),
    path('item/<int:item_id>', views.request_confirmation, name='request_view'),
    path('request/<int:item_id>', views.request_post, name='request_post'),
]
