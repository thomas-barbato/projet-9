"""import"""
import os

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projet9.settings")


class Ticket(models.Model):
    """docstring"""

    title = models.CharField(max_length=128)
    description = models.TextField(max_length=2048, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    image = models.ImageField(null=True, blank=True)
    time_created = models.DateTimeField("Created Time", auto_now_add=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """docstring"""
        return reverse("create_ticket_view")


class UserFollows(models.Model):
    """docstring"""

    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="following"
    )
    followed_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="followed_by"
    )

    def __str__(self):
        return self.user

    class Meta:
        """docstring"""

        unique_together = ("user", "followed_user")


class Review(models.Model):
    """docstring"""

    # need to search for a solution about null=True in FK...
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, null=True)
    rating = models.PositiveSmallIntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    headline = models.CharField(max_length=128)
    body = models.TextField(max_length=8192, blank=True)
    time_created = models.DateTimeField("Created Time", auto_now_add=True)

    def __str__(self):
        return self.headline

    def get_absolute_url(self):
        """docstring"""
        return reverse("posts_view")
