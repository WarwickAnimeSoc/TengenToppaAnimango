from django import forms


class SignupForm(forms.Form):
    signup_comment = forms.CharField(max_length=200)