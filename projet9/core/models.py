"""import"""
import os
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.urls import reverse

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projet9.settings")


class Ticket(models.Model):
    # TODO: Define Docstring
    """docstring"""

    title = models.CharField(max_length=128)

    description = models.TextField(max_length=2048, blank=True)

    # TODO: If the user is deleted, should we delete the ticket of the user as well?
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # TODO: Is blank necessary here?
    image = models.ImageField(null=True, blank=True)
    time_created = models.DateTimeField("Created Time", auto_now_add=True)

    def get_absolute_url(self):
        # TODO: Define Docstring
        """docstring"""
        return reverse("create_ticket_view")


class UserFollows(models.Model):
    # TODO: Define Docstring
    """docstring"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")
    followed_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followed_by")

    class Meta:
        # TODO: Define Docstring
        """docstring"""

        unique_together = ("user", "followed_user")


class Review(models.Model):
    # TODO: Define Docstring
    """docstring"""

    # need to search for a solution about null=True in FK...
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    # TODO: Is blank necessary here?
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    headline = models.CharField(max_length=128)
    # TODO: Is blank necessary here?
    body = models.TextField(max_length=8192, blank=True)
    time_created = models.DateTimeField("Created Time", auto_now_add=True)

    def get_absolute_url(self):
        # TODO: Define Docstring
        """docstring"""
        return reverse("posts_view")
