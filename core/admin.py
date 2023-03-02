from django.contrib import admin
from django.contrib.admin import ModelAdmin

from core.models import Review, Ticket, User, UserFollows


@admin.register(Review)
class ReviewAdmin(ModelAdmin):
    fields = ("rating", "headline", "body", "user")


@admin.register(Ticket)
class TicketAdmin(ModelAdmin):
    fields = ("title", "description", "image", "user")


@admin.register(UserFollows)
class UserFollowsAdmin(ModelAdmin):
    fields = ("user", "followed_user")
