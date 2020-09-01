from django.shortcuts import render, redirect


def home(request):
    return render(request, 'site_info/home.html')

# Redirect views, used to provide short links for other society pages


def discord(request):
    # Redirects to the society Discord server
    return redirect("https://discordapp.com/invite/GYM6ay7")


def facebook(request):
    # Redirects to the society Facebook group
    return redirect("https://facebook.com/groups/warwickanimesoc")


def warwicksu(request):
    # Redirects to the Warwick Students Union page for the society
    return redirect("https://warwicksu.com/societies-sports/societies/animeandmanga")


def malclub(request):
    # Redirects to the MyAnimeList Club for the society
    return redirect("https://myanimelist.net/clubs.php?cid=78196")
