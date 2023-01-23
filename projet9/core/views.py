from django.shortcuts import render, redirect, HttpResponseRedirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.views import View
from django.contrib.auth.decorators import login_required
from .forms import *
from .models import *
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime


class CreateUserView(View):
    template_name: str = "authentication/create_user.html"

    @method_decorator(csrf_exempt)
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {"signup_form": SignupForm})

    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        data = SignupForm(request.POST)
        print(data)
        if data.is_valid():
            if data.cleaned_data['password'] == data.cleaned_data['password2']:
                User.objects.create_user(
                    username=data.cleaned_data['username'],
                    password=data.cleaned_data['password'],
                    is_active=True,
                    is_staff=False,
                    date_joined=datetime.datetime.now()
                ).save()
            else:
                password_error = data.errors.as_data()['password']
                return render(request, self.template_name, {"signup_form": data})
        else:
            global_errors = data.errors.as_data()
            return redirect(reverse('create_user_view'))


class LoginView(View):
    template_name: str = "authentication/login.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {"signin_form": SigninForm, "error_display": "false"})
    
    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        if request.method == "POST":
            user = authenticate(
                request,
                username=request.POST.get("username"),
                password=request.POST.get("password"),
            )
            if user is not None:
                login(request, user)
                return redirect(reverse('dashboard_view'))
            else:
                return render(
                    request,
                    self.template_name,
                    {
                        "signin_form": SigninForm,
                        "error_display": "true",
                    },
                )

class DashboardView(LoginRequiredMixin, View):
    login_url = settings.LOGIN_URL
    template_name = "dashboard/dashboard.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
