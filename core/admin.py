# from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.admin import ModelAdmin

from core.models import Review, Ticket


@admin.register(Review)
class ReviewAdmin(ModelAdmin):
    pass


@admin.register(Ticket)
class TicketAdmin(ModelAdmin):
    pass
