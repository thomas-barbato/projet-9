from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.forms.widgets import PasswordInput, TextInput
from .validators.check_data import (
    CheckPasswordPolicy,
    CheckUsernameAlreadyUsed,
    CheckImageExtension,
)


class SigninForm(AuthenticationForm):
    username = forms.CharField(
        widget=TextInput(
            attrs={
                "label": "",
                "class": "form-control mb-1 form-input-text",
                "placeholder": "Nom d'utilisateur...",
            }
        ),
        required=True,
    )
    password = forms.CharField(
        widget=PasswordInput(
            attrs={
                "label": "",
                "class": "form-control form-input-text",
                "placeholder": "Mot de passe...",
            }
        ),
        required=True,
    )


class SignupForm(forms.Form):
    username = forms.CharField(
        widget=TextInput(
            attrs={
                "class": "form-control text-center",
                "placeholder": "Nom d'utilisateur",
            }
        ),
        required=True,
        label="",
        validators=[CheckUsernameAlreadyUsed().validate],
        help_text=CheckUsernameAlreadyUsed().get_help_text(),
    )
    password = forms.CharField(
        widget=PasswordInput(
            attrs={
                "class": "form-control mt-1 text-center",
                "placeholder": "Mot de passe",
            }
        ),
        required=True,
        label="",
        validators=[CheckPasswordPolicy().validate],
    )
    password2 = forms.CharField(
        widget=PasswordInput(
            attrs={
                "class": "form-control mt-1 text-center",
                "placeholder": "Confirmez le mot de passe",
            },
        ),
        required=True,
        label="",
        validators=[CheckPasswordPolicy().validate],
        help_text=CheckPasswordPolicy().get_help_text(),
    )


class CreateTicketForm(forms.Form):
    title = forms.CharField(
        widget=TextInput(attrs={}),
        required=True,
        label="",
    )
    description = forms.CharField(widget=TextInput(attrs={}), required=True)
    image = forms.ImageField(
        widget=forms.FileInput(attrs={}), validators=[CheckImageExtension().validate], required=True
    )


class CreateReviewForm(forms.Form):
    headline = forms.CharField(
        widget=TextInput(attrs={}),
        required=True,
        label="",
    )
    rating = forms.IntegerField(
        widget=TextInput(attrs={}),
        required=True,
        label="",
    )
    body = forms.CharField(
        widget=TextInput(attrs={}),
        required=True,
        label="",
    )
