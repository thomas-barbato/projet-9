"""imports"""
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.forms.widgets import PasswordInput, TextInput

from .helper.files import HandleUploadedFile
from .models import Review, Ticket
from .validators.check_data import (
    CheckImageExtension,
    CheckPasswordPolicy,
    CheckUsernameAlreadyUsed,
)


class SigninForm(AuthenticationForm):
    """docstring"""

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
    """docstring"""

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


class CreateTicketForm(forms.ModelForm):
    """docstring"""

    class Meta:
        model = Ticket
        fields = ["title", "description", "image", "user_id"]
        exclude = ["user_id"]

    image = forms.ImageField(
        widget=forms.FileInput(),
        validators=[CheckImageExtension().validate],
        required=True,
    )

    def save(self, *args, **kwargs):
        file = HandleUploadedFile(
            file=kwargs["file"],
            filename=kwargs["file"].name,
        )
        file.upload()
        self.instance.user = kwargs["user"]
        self.instance.image = file.get_filename()
        super().save()


class CreateReviewForm(forms.ModelForm):
    """docstring"""

    class Meta:
        model = Review
        fields = ["body", "headline", "rating", "user_id"]
        exclude = ["user_id"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["headline"].required = True
        self.fields["rating"].required = True
        self.fields["body"].required = True

    def save(self, *args, **kwargs):
        self.instance.user = kwargs["user"]
        self.instance.ticket_id = kwargs["ticket_id"]
        super().save()


class FollowUserForm(forms.Form):
    """docstring"""

    username = forms.CharField(
        widget=TextInput(),
        required=True,
        label="",
    )
