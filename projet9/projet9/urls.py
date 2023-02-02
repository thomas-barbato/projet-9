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
        "registration-success",
        core_views.SignupSuccessView.as_view(
            template_name="authentication/login.html"
        ),
        name="registration_success_view",
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
        "dashboard/posts/delete",
        core_views.DislayPostsView.delete,
        name="delete_post",
    ),
    path(
        "dashboard/posts/<int:post_id>/update",
        core_views.DislayPostsView.update_view,
        name="update_post_view",
    ),
    path(
        "dashboard/abonnements/",
        core_views.DisplaySuscribeView.as_view(
            template_name="dashboard/suscribe.html"
        ),
        name="suscribe_view",
    ),
    path(
        "logout",
        core_views.UserLogout.as_view(),
        name="user_logout",
    ),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
