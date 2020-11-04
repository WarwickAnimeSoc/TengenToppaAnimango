from django.contrib import messages
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.core.paginator import InvalidPage, Paginator
from django.contrib.auth.decorators import login_required

from apps.showings.models import Series
from .models import Item


def library_list(request, page):
    query = request.GET.get('query')
    category = request.GET.get('category')

    if query:
        series_list = Series.objects.filter(
            Q(item__isnull=False) & (Q(title_english__icontains=query) | Q(title_romaji__icontains=query))
        ).distinct().order_by('title_english')
    else:
        series_list = Series.objects.filter(item__isnull=False).distinct().order_by('title_english')

    if category == 'manga':
        series_list = series_list.filter(item__media_type='Manga')
    elif category == 'ln':
        series_list = series_list.filter(item__media_type='Light Novel')
    elif category == 'bd':
        series_list = series_list.filter(item__media_type='BD')
    elif category == 'dvd':
        series_list = series_list.filter(item__media_type='DVD')

    paginator = Paginator(series_list, 24)

    try:
        context_series_page = paginator.page(page)
    except InvalidPage:
        context_series_page = paginator.page(1)

    return render(request, 'library/list.html', context={'query': query, 'series_page': context_series_page})


def series_view(request, series_id):
    series = get_object_or_404(Series, id=series_id)
    if not series.item_set.all():
        # If the series doesn't have any items, then 404
        raise Http404()

    return render(request, 'library/series.html', context={'series': series})


@login_required
def request_confirmation(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    if request.method == 'POST':
        pass
    else:
        return render(request, 'library/request.html', context={'item': item})


@login_required
def request_post(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    # Create request
    if not item.request(request.user):
        messages.add_message(request, messages.ERROR, 'This item is not available.')
    else:
        messages.add_message(request, messages.SUCCESS, 'The item has been requested.')

    return redirect('library:series_view', series_id=item.parent_series.id)
