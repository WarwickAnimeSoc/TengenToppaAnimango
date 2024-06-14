from django.shortcuts import render

def anisoc_awards(request):
    return render(request, 'anisoc_awards/anisoc_awards.html')
