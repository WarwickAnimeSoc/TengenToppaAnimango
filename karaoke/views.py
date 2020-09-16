from django.shortcuts import render
from django.db.models import Q
from django.core.paginator import Paginator, InvalidPage
from django.contrib import messages

from .models import Song, Request
from .forms import KaraokeRequestForm


def karaoke_list(request, page):
    query = request.GET.get('query')

    if query:
        songs_list = Song.objects.filter(
            Q(title__icontains=query) | Q(artist__icontains=query) | Q(related_series__title_english__icontains=query)
            | Q(related_series__title_romaji__icontains=query)
        ).distinct().order_by('title')
    else:
        songs_list = Song.objects.filter().distinct().order_by('title')

    paginator = Paginator(songs_list, 24)

    try:
        context_songs_page = paginator.page(page)
    except InvalidPage:
        context_songs_page = paginator.page(1)

    return render(request, 'karaoke/list.html', context={'query': query, 'songs_page': context_songs_page})


def request_song(request):
    requests_list = Request.objects.filter().distinct().order_by("title")
    context = {'requests': requests_list}

    if request.method == 'POST':
        form = KaraokeRequestForm(request.POST)
        if form.is_valid():
            form.submit()
            messages.add_message(request, messages.SUCCESS, 'Your request has been submitted!')
        else:
            form_errors = form.non_field_errors()
            if form_errors:
                # Either the request is a duplicate or the song is already in the list
                for error in form_errors:
                    messages.add_message(request, messages.ERROR, error)
            else:
                messages.add_message(request, messages.ERROR, 'Please correct the errors below')
            context['form'] = form
            return render(request, 'karaoke/request.html', context=context)
    return render(request, 'karaoke/request.html', context=context)


def mapping_guide(request):
    return render(request, 'karaoke/guide.html')