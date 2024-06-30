"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    # Apps Urls
    path('', include('apps.miscellaneous.urls')),
    path('members/', include('apps.members.urls')),
    path('events/', include('apps.events.urls')),
    path('showings/', include('apps.showings.urls')),
    path('news/', include('apps.news.urls')),
    path('karaoke/', include('apps.karaoke.urls')),
    path('history/', include('apps.history.urls')),
    path('archive/', include('apps.archive.urls')),
    path('library/', include('apps.library.urls')),
    path('anisoc_awards/', include('apps.anisoc_awards.urls')),
    # API Urls
    path('api/library/', include('apps.library.api.urls')),
    path('api/events/', include('apps.events.api.urls')),
    # Django Urls
    path('admin/', admin.site.urls),
    path('martor/', include('martor.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
