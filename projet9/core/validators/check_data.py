from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django.contrib.auth.models import User
import re


class CheckPasswordStrength:
    def __init__(self):
        self.password_pattern = (
            "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$"
        )

    def validate(self, password):
        """
        Has minimum 8 characters in length
        At least one uppercase letter. You can remove this condition by removing (?=.*?[A-Z])
        At least one lowercase letter. You can remove this condition by removing (?=.*?[a-z])
        At least one digit. You can remove this condition by removing (?=.*?[0-9])
        At least one special character, You can remove this condition by removing (?=.*?[#?!@$%^&*-])
        """
        if re.match(self.password_pattern, password) is None:
            raise ValidationError(
                _(mark_safe(
                    '<div class="alert alert-danger text-center col-xl-4 col-md-4 col-sm-12" role="alert">'
                        '<p><b>Ce mot de passe doit contenir à minima:</b></p>'
                        '<p><b>8</b> caractères</p>'
                        '<p><b>1</b> majuscule</p>'
                        '<p><b>1</b> minuscule</p>'
                        '<p><b>1</b> symbole</p>'
                        '<p><b>1</b> chiffre</p>'
                    '</div>'
                )),
                code="password_too_weak",
            )

    def get_help_text(self):
        return _(
            '<div class="alert alert-dark" role="alert">'
            '<ul>'
                '<li><b>Ce mot de passe doit contenir à minima:</b></li>'
                '<li><b>8</b> caractères</li>'
                '<li><b>1</b> majuscule</li>'
                '<li><b>1</b> minuscule</li>'
                '<li><b>1</b> symbole</li>'
                '<li><b>1</b> chiffre</li>'
            '</ul>'
            '</div>'
        )



class CheckUsernameAlreadyUsed:
    def __init__(self):
        self.table = User
        
    def validate(self, user):
        """
            check if username already exists in db.
        """
        if self.table.objects.filter(username=user).exists() is True:
            raise ValidationError(
                _(mark_safe(
                    '<div class="alert alert-danger text-center col-xl-4 col-md-4 col-sm-12" role="alert">'
                        '<p><b><i class=' + '"fas fa-exclamation-triangle"' + '></i> Votre nom doit être unique.</b></p>'
                    '</div>'
                )),
                code="username_already_used",
            )

    def get_help_text(self):
        return _(
            '<div class="alert alert-danger text-center col-xl-4 col-md-4 col-sm-12" role="alert">'
            '<ul>'
                '<li><b><i class=' + '"fas fa-exclamation-triangle"' + '></i> Votre nom d\'utilisateur doit être unique.</b></li>'
            '</ul>'
            '</div>'
        )
            
