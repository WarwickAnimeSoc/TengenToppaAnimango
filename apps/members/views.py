from urllib.parse import quote_plus
import socket
from django.conf import settings
import requests
from apps.members.models import Member
from django.http import HttpRequest, HttpResponse
from smtplib import SMTPAuthenticationError

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from apps.library.models import Request, ArchivedRequest
from .forms import ProfileEditForm, OverridePasswordChangeForm, OverridePasswordRestForm


def login_view(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                messages.add_message(request, messages.SUCCESS, 'You have been logged in')
                return redirect('miscellaneous:home')
            else:
                messages.add_message(request, messages.ERROR, 'Your account has been disabled')
                return render(request, 'members/login.html')
        else:
            messages.add_message(request, messages.ERROR, 'Incorrect username or password')
            return render(request, 'members/login.html', context={'username': username})
    else:
        return render(request, 'members/login.html')


@login_required
def profile(request: HttpRequest) -> HttpResponse:
    current_requests = Request.objects.select_related().filter(user=request.user).order_by('-return_deadline')
    archived_requests = ArchivedRequest.objects.select_related().filter(user=request.user).order_by('-date_requested')

    context = {'current_requests': current_requests, 'archived_requests': archived_requests}
    return render(request, 'members/profile.html', context=context)


@login_required
def profile_edit(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES)
        if form.is_valid():
            user_member: Member = request.user.member
            user_member.nickname = form.cleaned_data['nickname']
            user_member.show_full_name = form.cleaned_data['show_full_name']
            user_member.discord_username = form.cleaned_data['discord_username']
            if form.cleaned_data['avatar_image'] is not None:
                user_member.avatar_image = form.cleaned_data['avatar_image']
            user_member.save()
            messages.add_message(request, messages.SUCCESS, 'Your profile has been successfully updated')
            return redirect('members:profile')
        else:
            messages.add_message(request, messages.ERROR, 'There was a problem updating your profile')
            return render(request, 'members/edit.html', context={'form': form})
    else:
        return render(request, 'members/edit.html', )


# NOTE: not production ready
REDIRECT_URI = "https://animesoc.co.uk/members/verify/discord"

# NOTE: not production ready
@login_required
def link_discord(request: HttpRequest) -> HttpResponse:
    return redirect(f"https://discord.com/oauth2/authorize?client_id={settings.DISCORD_CLIENT_ID}&response_type=code&redirect_uri={quote_plus(REDIRECT_URI)}&scope=identify&prompt=consent")


# NOTE: not production ready
@login_required
def verify_discord(request: HttpRequest) -> HttpResponse:
    code = request.GET.get("code")

    # get access token
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    r = requests.post("https://discord.com/api/v10/oauth2/token", data=data, headers=headers, auth=(settings.DISCORD_CLIENT_ID, settings.DISCORD_CLIENT_SECRET))
    r.raise_for_status()
    token = r.json().get('access_token')

    headers = {
        'Authorization': f"Bearer {token}"
    }

    r = requests.get("https://discord.com/api/v10/users/@me", headers=headers)
    r.raise_for_status()
    json = r.json()
    discord_id = json.get('id')
    discord_username = json.get('username')


    member: Member = request.user.member
    member.discord_id = discord_id
    member.discord_username = discord_username
    member.save()
    
    # revoke token
    data = {
        'token': token,
        'token_type_hint': 'access_token',
    }

    headers = {
         'Content-Type': 'application/x-www-form-urlencoded'
    }

    r = requests.post("https://discord.com/api/v10/oauth2/token/revoke", data=data, headers=headers, auth=(settings.DISCORD_CLIENT_ID, settings.DISCORD_CLIENT_SECRET))

    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.settimeout(2)
        sock.connect(settings.ANIMADEUS_SOCK)
        sock.sendall(f"memberfy {discord_id}".encode())

    return redirect('members:edit')

    
@login_required
def change_password(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = OverridePasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.add_message(request, messages.SUCCESS, 'Your password was successfully updated')
            return redirect('members:profile')
        else:
            messages.add_message(request, messages.ERROR, 'There was a problem updating your password')
            return render(request, 'members/password_change.html', context={'form': form})
    else:
        return render(request, 'members/password_change.html')


@login_required
def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    messages.add_message(request, messages.WARNING, 'You have been logged out')
    return redirect('miscellaneous:home')


def forgot_password(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = OverridePasswordRestForm(request.POST)
        if form.is_valid():
            # We use Gmail to send emails from the website. Google recognizes django as a "less secure app" meaning
            # that it will block login attempts from django causing an SMTPAuthenticationError. Enabling less secure
            # apps https://myaccount.google.com/u/1/lesssecureapps will fix the issue, however this setting will be
            # automatically disabled if it goes unused for a while.
            try:
                form.save(request=request, email_template_name='reset_password_email/reset_password_email.html',
                          subject_template_name='reset_password_email/reset_password_email_subject.txt',)
                messages.add_message(request, messages.SUCCESS,
                                     'You have been sent an email with instructions to reset your password')
            except SMTPAuthenticationError:
                messages.add_message(request, messages.ERROR,
                                     'There has been an error sending the email. Please contact the webmaster.')
            return redirect('miscellaneous:home')
        else:
            return render(request, 'members/forgot_password.html', context={'form': form})
    else:
        return render(request, 'members/forgot_password.html')


def password_reset_redirect(request: HttpRequest) -> HttpResponse:
    messages.add_message(request, messages.SUCCESS,
                         'Your password has been reset. You can now log in using your new password.')
    return redirect('miscellaneous:home')
