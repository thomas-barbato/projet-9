from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
# authentication/urls.py
from django.contrib.auth.views import LoginView
import core
from core import views

urlpatterns = [
   path('admin', admin.site.urls, name="admin"),
   path('', LoginView.as_view(
       template_name='authentication/login.html',
       redirect_authenticated_user=True
   ), name='login')
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)