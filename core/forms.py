"""imports"""
import datetime

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import make_password
from django.forms.widgets import PasswordInput, TextInput

from .helper.files import HandleUploadedFile
from .models import Review, Ticket, User
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


class SignupForm(forms.ModelForm):
    """docstring"""

    class Meta:
        model = User
        fields = ["username", "password"]
        exclude = ["user_id"]

    def save(self, *args, **kwargs):
        self.instance.password = make_password(self.instance.password)
        self.instance.is_staff = False
        self.instance.is_active = True
        self.instance.date_joined = datetime.datetime.now()
        super().save()

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


class UpdateTicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ["title", "description", "image", "user_id"]
        exclude = ["user_id"]

    def save(self, *args, **kwargs):
        if "file" in kwargs:
            file = HandleUploadedFile(
                file=kwargs["file"]["image"],
                filename=kwargs["file"]["image"].name,
            )
            ticket = Ticket.objects.get(id=kwargs["id"], user_id=kwargs["user_id"])
            HandleUploadedFile().delete_standalone_img(filename=ticket.image)
            file.upload()
            self.instance.image = file.get_filename()
        super().save()


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
