from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

# authentication/urls.py
from django.contrib.auth.views import LoginView
import core
from core import views as core_views

app_name = 'core'

urlpatterns = [
    path("admin", admin.site.urls, name="admin"),
    path(
        "",
        core_views.LoginView.as_view(template_name="authentication/login.html"),
        name="login_view",
    ),
    path(
        "new-user",
        core_views.CreateUserView.as_view(template_name="authentication/create_user.html"),
        name="create_user_view",
    ),
    path(
        "dashboard",
        core_views.DashboardView.as_view(template_name="dashboard/dashboard.html"),
        name="dashboard_view",
    ),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
