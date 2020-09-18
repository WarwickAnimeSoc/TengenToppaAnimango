from django.shortcuts import render, reverse
from django.core.paginator import Paginator, InvalidPage
from django.db.models import Q
from django.utils import timezone

from .models import Showing, Series


def showings(request, page):
    query = request.GET.get('query')

    paginator = Paginator(get_showings(query), 12)
    try:
        context_showings_page = paginator.page(page)
    except InvalidPage:
        context_showings_page = paginator.page(1)

    return render(request, 'showings/list.html', context={'query': query, 'showings_page': context_showings_page})


def get_showings(query):
    showing_objects = Showing.objects
    # Removed search by year from aniMango as I don't really see the point in it.
    if query:
        showing_objects = showing_objects.filter(Q(show__series__title_romaji__icontains=query) or
                                                 Q(show__series__title_english__icontains=query)).distinct()
    return showing_objects.order_by('-date')


def cooldown_dashboard(request):
    # Anyone can see this view with the URL as it doesn't contain anything sensitive, but only exec will have it
    # linked in their navbar.
    series_objects = Series.objects

    # Get cooldown groups
    all_cooldown = series_objects.filter(
        Q(cooldown_end_date__gte=timezone.now())).distinct().order_by('cooldown_end_date')
    global_cooldown = all_cooldown.filter(Q(last_shown_instance__show_type__in=['mv', 'ms', 'mc']))
    exec_choice_cooldown = all_cooldown.filter(Q(last_shown_instance__show_type__in=['ex']))

    context = {
        'global_cooldown': global_cooldown,
        'exec_choice_cooldown': exec_choice_cooldown
    }

    return render(request, 'showings/cooldown_dashboard.html', context=context)
