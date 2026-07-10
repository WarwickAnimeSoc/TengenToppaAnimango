from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

def anisoc_awards(request: HttpRequest) -> HttpResponse:
    return render(request, 'anisoc_awards/anisoc_awards.html')
