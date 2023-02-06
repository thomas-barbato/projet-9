import datetime
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.urls import reverse



import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projet9.settings")


class Ticket(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField(max_length=2048, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(null=True, blank=True)
    time_created = models.DateTimeField("Created Time", auto_now_add=True)

    def get_absolute_url(self):
        return reverse('create_ticket_view')


class UserFollows(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following"
    )
    followed_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="followed_by"
    )

    class Meta:
        unique_together = ("user", "followed_user")


class Review(models.Model):
    # need to search for a solution about null=True in FK...
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True
    )
    headline = models.CharField(max_length=128)
    body = models.TextField(max_length=8192, blank=True)
    time_created = models.DateTimeField("Created Time", auto_now_add=True)

    def get_absolute_url(self):
        return reverse('posts_view')
