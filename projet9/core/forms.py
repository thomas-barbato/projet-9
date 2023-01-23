from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.forms.widgets import PasswordInput, TextInput
from .validators.check_data import CheckPasswordStrength, CheckUsernameAlreadyUsed
from django.utils.safestring import mark_safe


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
        help_text=CheckUsernameAlreadyUsed().get_help_text()
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
        validators=[CheckPasswordStrength().validate],
    )
    password2 = forms.CharField(
        widget=PasswordInput(
            attrs={
                "class": "form-control text-center",
                "placeholder": "Confirmez le mot de passe",
            },
        ),
        required=True,
        label="",
        validators=[CheckPasswordStrength().validate],
        help_text=CheckPasswordStrength().get_help_text()
    )
