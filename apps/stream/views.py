from django.shortcuts import render, redirect
from django.conf import settings
from django.utils import timezone

from .models import ViewCounter, View


def stream(request):
    hls_stream_url = settings.HLS_STREAM_URL
    return render(request, 'stream/stream.html', context={'stream_source': hls_stream_url})


def viewcount(request):
    if request.user.is_staff:
        view_counter = ViewCounter.objects.get(id=1)
        view_counter.prune()
        view_counter.save()
        return render(request, 'stream/viewcount.html', context={'views': view_counter.count()})
    else:
        return render(request, '403.html')


def viewtick(request):
    view_counter = ViewCounter.objects.get(id=1)
    token = request.GET.get('token')
    print(token)
    if token:
        try:
            view_object = View.objects.get(token=token)
            view_object.last_update = timezone.now()
        except View.DoesNotExist:
            view_object = View(related_counter=view_counter, token=token, last_updated=timezone.now())
        view_object.save()

    return redirect('stream:stream')
