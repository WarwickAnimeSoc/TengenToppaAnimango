from smtplib import SMTPAuthenticationError

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .forms import ProfileEditForm, OverridePasswordChangeForm, OverridePasswordRestForm


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                messages.add_message(request, messages.SUCCESS, 'You have been logged in')
                return redirect('site_info:home')
            else:
                messages.add_message(request, messages.ERROR, 'Your account has been disabled')
                return render(request, 'members/login.html')
        else:
            messages.add_message(request, messages.ERROR, 'Incorrect username or password')
            return render(request, 'members/login.html', context={'username': username})
    else:
        return render(request, 'members/login.html')


@login_required
def profile(request):
    # TODO: Add library items
    return render(request, 'members/profile.html')


@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES)
        if form.is_valid():
            user_member = request.user.member
            user_member.nickname = form.cleaned_data['nickname']
            user_member.show_full_name = form.cleaned_data['show_full_name']
            user_member.discord_tag = form.cleaned_data['discord_tag']
            if form.cleaned_data['avatar_image'] is not None:
                user_member.avatar_image = form.cleaned_data['avatar_image']
            user_member.save()
            messages.add_message(request, messages.SUCCESS, 'Your profile has been successfully updated')
            return redirect('members:profile')
        else:
            messages.add_message(request, messages.ERROR, 'There was a problem updating your profile')
            return render(request, 'members/edit.html', context={'form': form})
    else:
        return render(request, 'members/edit.html',)


@login_required
def change_password(request):
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
def logout_view(request):
    logout(request)
    messages.add_message(request, messages.WARNING, 'You have been logged out')
    return redirect('site_info:home')


def forgot_password(request):
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
            return redirect('site_info:home')
        else:
            return render(request, 'members/forgot_password.html', context={'form': form})
    else:
        return render(request, 'members/forgot_password.html')


def password_reset_redirect(request):
    messages.add_message(request, messages.SUCCESS,
                         'Your password has been reset. You can now log in using your new password.')
    return redirect('site_info:home')