from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views

from . import views
from .forms import OverrideSetPasswordForm

app_name = 'members'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('profile/', views.profile, name='profile'),
    path('edit/', views.profile_edit, name='edit'),
    path('change_password/', views.change_password, name='change_password'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    # Only using default auth view for password resets as the others required overwrites.
    path('reset_password/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='members/templates/members/reset_password.html',
                                                     form_class=OverrideSetPasswordForm,
                                                     success_url=reverse_lazy('members:password_reset_redirect')
                                                     ),
         name='password_reset_confirm'),
    path('reset_password/done/', views.password_reset_redirect, name='password_reset_redirect')
]