from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.core.paginator import Paginator, InvalidPage
from django.contrib import messages

from .models import Event, Signup
from .forms import SignupForm


def upcoming_events(request, page):
    return render(request, 'events/list.html', get_event_context(page, 'Upcoming'))


def previous_events(request, page):
    return render(request, 'events/list.html', get_event_context(page, 'Previous'))


def get_event_context(paginator_page, event_type):
    # Possible event_types are:
    # Upcoming - An event that has yet to start.
    # Previous - An event that has already ended.
    if event_type == 'Upcoming':
        context_events = Event.objects.filter(event_start_date__gte=timezone.now()).order_by('event_start_date')
    else:
        context_events = Event.objects.filter(event_end_date__lte=timezone.now()).order_by('-event_end_date')

    ongoing_events = Event.objects.filter(event_start_date__lte=timezone.now(),
                                          event_end_date__gte=timezone.now()).order_by('event_end_date')

    # Only previous or upcoming events are paginated. Ongoing events will always be displayed at the top of the page.
    # This is done under the assumption that there will only ever be 1 - 2 ongoing events.
    paginator = Paginator(context_events, 12)
    try:
        context_events_page = paginator.page(paginator_page)
    except InvalidPage:
        context_events_page = paginator.page(1)

    return {'ongoing_events': ongoing_events, 'events_page': context_events_page, 'events_type': event_type}


def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    signups = Signup.objects.filter(event=event).order_by("-created")
    # already_signed_up has to be set outside the template, as it requires a parameter to return a result.
    already_signed_up = request.user.is_authenticated and event.already_signed_up(request.user.member)
    context = {'event': event, 'signups': signups, 'already_signed_up': already_signed_up}

    # Exec are allowed to sign-up before the event has opened to everyone else.
    if event.signups_open_date and not event.signups_open() and request.user.is_staff:
        messages.add_message(request, messages.WARNING,
                             'Signups for this event are not yet open to regular members.'
                             ' However, as Exec you can signup early.')

    if request.method == 'POST':
        form = SignupForm(request.POST)
        context['form'] = form
        if request.user.is_authenticated:
            if event.is_full():
                messages.add_message(request, messages.ERROR, 'This event is full')
            elif not event.signup_required():
                messages.add_message(request, messages.ERROR, 'This event does not require signups')
            elif event.already_signed_up(request.user.member):
                messages.add_message(request, messages.ERROR, 'You have already signed up for this event')
            elif event.signups_closed():
                messages.add_message(request, messages.ERROR, 'Signups for this event have closed')
            elif not event.signups_open() and not request.user.is_staff:
                messages.add_message(request, messages.ERROR, 'Signups for this event have not opened yet')
            elif not form.is_valid():
                messages.add_message(request, messages.ERROR, 'Unable to sign you up, please correct the issues below')
            else:
                signup = Signup(member=request.user.member, event=event, comment=form.cleaned_data['signup_comment'],
                                created=timezone.now())
                signup.save()
                messages.add_message(request, messages.SUCCESS, 'You have been signed up')
                context['already_signed_up'] = True
            return render(request, 'events/event_detail.html', context=context)
        else:
            messages.add_message(request, messages.ERROR, 'Please login first')
    return render(request, 'events/event_detail.html', context=context)


@login_required
def cancel_signup(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if event.signups_closed():
        messages.add_message(request, messages.ERROR, 'Signups for this event have closed')
    else:
        Signup.objects.filter(event=event, member=request.user.member).delete()
        messages.add_message(request, messages.SUCCESS, 'Cancellation successful')
    return redirect('events:event_detail', event_id=event_id)