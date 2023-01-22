from django.shortcuts import render, redirect, HttpResponseRedirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.views import View
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from .forms import *
from .models import *
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.utils.decorators import method_decorator


class CreateUserView(View):
    template_name: str = "authentication/create_user.html"

    @method_decorator(csrf_exempt)
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {"signup_form": SignupForm})


class LoginView(View):
    template_name: str = "authentication/login.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {"signin_form": SigninForm, "error_display": "false"})

    def post(self, request, *args, **kwargs):
        if request.method == "POST":
            user = authenticate(
                request,
                username=request.POST.get("username"),
                password=request.POST.get("password"),
            )
            if user is not None:
                login(request, user)
                return self.redirect_to_dashboard()
            else:
                return render(
                    request,
                    self.template_name,
                    {
                        "signin_form": SigninForm,
                        "error_display": "true",
                    },
                )

    @method_decorator(login_required)
    def redirect_to_dashboard(self):
        return HttpResponseRedirect("dashboard")


class DashboardView(LoginRequiredMixin, View):
    login_url = settings.LOGIN_URL
    template_name = "dashboard/dashboard.html"
