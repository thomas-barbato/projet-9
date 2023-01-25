from channels.generic.websocket import AsyncWebsocketConsumer
from django.shortcuts import render, redirect, HttpResponseRedirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.views import View
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session
from django.views.generic import RedirectView
from .forms import *
from .models import *
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django import forms
import datetime
import json
from .classes.files import HandleUploadedFile


class CreateUserView(View):
    template_name: str = "authentication/create_user.html"

    @method_decorator(csrf_exempt)
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {"signup_form": SignupForm})

    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        data = SignupForm(request.POST)
        response = ""
        if data.is_valid():
            if data.cleaned_data["password"] == data.cleaned_data["password2"]:
                User.objects.create_user(
                    username=data.cleaned_data["username"],
                    password=data.cleaned_data["password"],
                    is_active=True,
                    is_staff=False,
                    date_joined=datetime.datetime.now(),
                ).save()
                response = {'status': 1, 'url_redirect': "registration_success_view"}
                return JsonResponse(
                    response
                )
            else:
                data.add_error(
                    None,
                    '<div class="alert alert-danger text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
                    '<p>Veuillez entrer deux fois le même mot de passe.</p>'
                    '</div>',
                )
                response = {'status': 0, 'errors': dict(data.errors.items())}
                return JsonResponse(
                    response
                )
        else:
            response = {'status': 0, 'errors': dict(data.errors.items())}
            return JsonResponse(
                response
            )


class SignupSuccessView(View):
    login_url = settings.LOGIN_URL
    template_name = "dashboard/flux.html"

    def get(self, request, *args, **kwargs):
        return render(
            request,
            self.template_name,
            {"signin_form": SigninForm, "user_creation_success": "true"},
        )

class LoginView(View):
    template_name: str = "authentication/login.html"

    def get(self, request, *args, **kwargs):
        return render(
            request,
            self.template_name,
            {"signin_form": SigninForm, "error_display": "false"},
        )

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
                response = {'status': 1}
                return JsonResponse(
                    response
                )
            else:
                response = {'errors': "true"}
                return JsonResponse(
                    response
                )
        else:
            response = {'errors': "true"}
            return JsonResponse(
                response
            )


class FluxView(LoginRequiredMixin, View):
    login_url = settings.LOGIN_URL
    template_name = "dashboard/flux.html"
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class CreateTicketView(LoginRequiredMixin, View):
    login_url = settings.LOGIN_URL
    template_name = "dashboard/create_ticket.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    
    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        form = CreateTicketForm(request.POST, request.FILES)
        if form.is_valid():
            HandleUploadedFile(request.FILES['image'], request.FILES['image'].name)
            Ticket.objects.create(
                title = form.cleaned_data["title"],
                description = form.cleaned_data["description"],
                user_id = request.user.id,
                image = request.FILES['image'].name,
            )
            return render(request, "dashboard/flux.html")
        else:
            # A FAIRE !
            print("non")


class UserLogout(RedirectView):
    login_url = settings.LOGIN_URL
    template_name: str = "authentication/login.html"

    def get(self, request, *args, **kwargs):
        logout(request)
        return render(
            request,
            self.template_name,
            {"signin_form": SigninForm, "error_display": "false"},
        )
        