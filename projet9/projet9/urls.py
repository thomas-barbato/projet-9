from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

# authentication/urls.py
from django.contrib.auth.views import LoginView
import core
from core import views as core_views

app_name = "core"

urlpatterns = [
    path("admin", admin.site.urls, name="admin"),
    path(
        "",
        core_views.LoginView.as_view(template_name="authentication/login.html"),
        name="login_view",
    ),
    path(
        "registration",
        core_views.CreateUserView.as_view(
            template_name="authentication/create_user.html"
        ),
        name="registration_view",
    ),
    path(
        "dashboard/flux",
        core_views.FluxView.as_view(template_name="dashboard/flux.html"),
        name="flux_view",
    ),
    path(
        "dashboard/create_ticket",
        core_views.CreateTicketView.as_view(
            template_name="dashboard/create_ticket.html"
        ),
        name="create_ticket_view",
    ),
    path(
        "dashboard/ticket/<int:pk>",
        core_views.UpdateTicket.as_view(
            template_name="dashboard/update_ticket.html"
        ),
        name="update_ticket_view",
    ),
    path(
        "dashboard/ticket/delete/<int:pk>",
        core_views.DeleteTicket.as_view(template_name="dashboard/posts.html"),
        name="delete_ticket",
    ),
    path(
        "dashboard/create_review",
        core_views.CreateFullReviewView.as_view(
            template_name="dashboard/create_review.html"
        ),
        name="create_review_view",
    ),
    path(
        "dashboard/create_answer_review/<int:id>",
        core_views.CreateReviewView.as_view(
            template_name="dashboard/create_answer_review.html"
        ),
        name="answer_review_view",
    ),
    path(
        "dashboard/posts/",
        core_views.DislayPostsView.as_view(
            template_name="dashboard/posts.html"
        ),
        name="posts_view",
    ),
    path(
        "dashboard/posts/delete/<int:pk>",
        core_views.DeletePost.as_view(template_name="dashboard/posts.html"),
        name="delete_post",
    ),
    path(
        "dashboard/posts/<int:pk>",
        core_views.UpdatePost.as_view(
            template_name="dashboard/update_post.html"
        ),
        name="update_post_view",
    ),
    path(
        "dashboard/suscribe/",
        core_views.DisplaySuscribeView.as_view(
            template_name="dashboard/suscribe.html"
        ),
        name="suscribe_view",
    ),
    path(
        "dashboard/suscribe/delete/<int:pk>",
        core_views.UnfollowUser.as_view(
            template_name="dashboard/suscribe.html"
        ),
        name="unfollow_user",
    ),
    path(
        "logout",
        core_views.UserLogout.as_view(),
        name="user_logout",
    ),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
