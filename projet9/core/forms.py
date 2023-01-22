from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.forms.widgets import PasswordInput, TextInput


class SigninForm(AuthenticationForm):
    username = forms.CharField(
        widget=TextInput(
            attrs={
                "class": 'form-control mb-1 form-input-text required="required"',
                "placeholder": "Nom d'utilisateur...",
            }
        )
    )
    password = forms.CharField(
        widget=PasswordInput(
            attrs={
                "class": 'form-control form-input-text required="required"',
                "placeholder": "Mot de passe...",
            }
        ),
    )


class SignupForm(forms.Form):
    username = forms.CharField(
        widget=TextInput(
            attrs={"class": "form-control", "placeholder": "Nom d'utilisateur..."}
        )
    )
    password = forms.CharField(
        widget=PasswordInput(
            attrs={"class": "form-control", "placeholder": "Mot de passe..."}
        )
    )
