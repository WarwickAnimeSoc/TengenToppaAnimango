from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm, SetPasswordForm


class ProfileEditForm(forms.Form):
    discord_tag_validator_message = '''Invalid format. Your discord tag should be your username followed by a # and your 
    4 digit identifier, i.e LittleDemon#0713.'''
    discord_tag_validator = RegexValidator(r'^[a-zA-Z0-9_-]{2,32}$', message=discord_tag_validator_message)

    nickname = forms.CharField(label="Nickname", max_length=30, required=False)
    show_full_name = forms.BooleanField(label="Show full name", required=False)
    discord_tag = forms.CharField(label="Discord tag", max_length=40, validators=[discord_tag_validator],
                                  required=False)
    avatar_image = forms.ImageField(label="Avatar image", required=False)

    def clean_avatar_image(self):
        image = self.cleaned_data['avatar_image']
        # Images should less than 2Mb or 2097152 bytes
        if image is not None:
            if image.size > 2097152:
                size_error = ValidationError('Upload a smaller image. The file you uploaded was too large.',
                                             code='invalid_image')
                self.add_error('avatar_image', size_error)
            if image.content_type not in ['image/png', 'image/jpeg']:
                type_error = ValidationError('Incorrect image format. Your image must be a .png, .jpg or .jpeg file.',
                                             code='invalid_image')
                self.add_error('avatar_image', type_error)

        return image


# The Override forms below are used to override the default authentication forms and remove the widgets. This allows
# the default forms to be used with the custom styles on the site.


class OverridePasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label='Old password', strip=False)
    new_password1 = forms.CharField(label='New password', strip=False)
    new_password2 = forms.CharField(label='New password confirmation', strip=False)


class OverridePasswordRestForm(PasswordResetForm):
    email = forms.EmailField(label='Email', max_length=254)


class OverrideSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(label='New password', strip=False)
    new_password2 = forms.CharField(label='New password confirmation', strip=False)