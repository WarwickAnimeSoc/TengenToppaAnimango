from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib import messages

from apps.events.models import Event
from apps.news.models import Article
from .models import HomeAlert


def home(request):
    # Homepage should display a certain amount of upcoming event, ongoing events and articles
    ongoing_events = Event.objects.filter(event_start_date__lte=timezone.now(),
                                          event_end_date__gte=timezone.now()).order_by('event_end_date')
    upcoming_events = Event.objects.filter(event_start_date__gte=timezone.now()).order_by('event_start_date')
    recent_articles = Article.objects.filter().order_by('-created')

    try:
        alert = HomeAlert.objects.last()
    except HomeAlert.DoesNotExist:
        alert = None

    # Set limits here
    ongoing_events = ongoing_events[:3]
    upcoming_events = upcoming_events[:3]
    recent_articles = recent_articles[:3]

    context = {
        'ongoing_events': ongoing_events,
        'upcoming_events': upcoming_events,
        'recent_articles': recent_articles,
        'alert': alert
    }

    return render(request, 'miscellaneous/home.html', context=context)


def privacy(request):
    return render(request, 'miscellaneous/privacy.html')

# Redirect views, used to provide short links for other society pages


def discord(request):
    # Redirects to the society Discord server
    return redirect('https://discord.gg/JaYTGfu')


def facebook(request):
    # Redirects to the society Facebook group
    return redirect('https://facebook.com/groups/warwickanimesoc')


def warwicksu(request):
    # Redirects to the Warwick Students Union page for the society
    return redirect('https://warwicksu.com/societies-sports/societies/animeandmanga')


def malclub(request):
    # Redirects to the MyAnimeList Club for the society
    return redirect('https://myanimelist.net/clubs.php?cid=78196')


def github(request):
    # Redirects to the Github repo for the site
    return redirect('https://github.com/Danalite/TengenToppaAnimango')


def streamguide(request):
    # Redirects to the discord/stream guide
    return redirect('https://docs.google.com/document/d/1KsUpA6euakmBq09rXux_HK0TTEog45C49pByP4iVjCg/edit')


def election(request):
    # Redirects to the article on the elections. The URL probably shouldn't be hardcoded, but this
    # is temporary so it should be fine.
    return redirect('https://animesoc.co.uk/news/article/87/2021-exec-elections')
