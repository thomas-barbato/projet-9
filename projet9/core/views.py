from channels.generic.websocket import AsyncWebsocketConsumer
from django.shortcuts import render, redirect, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.views import View
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
import datetime
import json
from .classes.files import HandleUploadedFile
from django.contrib import messages
from django.forms.models import model_to_dict


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
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    '<div class="alert alert-success text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
                    "<p>Vous êtes maintenant inscrit.</p>"
                    "</div>",
                )
                response = {"status": 1}
                return JsonResponse(response)
            else:
                data.add_error(
                    None,
                    '<div class="alert alert-danger text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
                    "<p>Veuillez entrer deux fois le même mot de passe.</p>"
                    "</div>",
                )
                response = {"status": 0, "errors": dict(data.errors.items())}
                return JsonResponse(response)
        else:
            response = {"status": 0, "errors": dict(data.errors.items())}
            return JsonResponse(response)


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
                response = {"status": 1}
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    '<div class="alert alert-success text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
                    "<p>Vous êtes maintenant connecté.</p>"
                    "</div>",
                )
                return JsonResponse(response)
            else:
                response = {"errors": "true"}
                return JsonResponse(response)
        else:
            response = {"errors": "true"}
            return JsonResponse(response)


class FluxView(LoginRequiredMixin, View):
    login_url = settings.LOGIN_URL
    template_name = "dashboard/flux.html"

    def get(self, request, *args, **kwargs):
        query_review = [result for result in Review.objects.select_related('user', 'ticket','ticket__user_id', 'user__username').values(
            'headline',
            'body',
            'rating',
            'time_created',
            'ticket_id',
            'user_id',
            'user__username',
            'ticket__image',
            'ticket__title',
            'ticket__user_id__username'
        ).order_by('-time_created')]

        review = [dict(item, is_review=True) for item in query_review]

        query_ticket = [result for result in Ticket.objects.select_related('user').values(
            'id',
            'title',
            'description',
            'image',
            'user_id',
            'user__username',
            'time_created'
        ).order_by('-time_created')]

        ticket = [dict(item, is_ticket=True) for item in query_ticket]

        result = []
        ticket.extend(review)
        for item in ticket:
            if item not in result:
                result.append(item)

        result = sorted(result, key=lambda d: d['time_created'], reverse=True)
        return render(request, self.template_name, {'posts': result, 'star_range': range(5)})


class CreateTicketView(LoginRequiredMixin, View):
    login_url = settings.LOGIN_URL
    template_name = "dashboard/create_ticket.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        form = CreateTicketForm(request.POST, request.FILES)
        if form.is_valid():
            file = HandleUploadedFile(request.FILES["image"], request.FILES["image"].name)
            Ticket.objects.create(
                title=form.cleaned_data["title"],
                description=form.cleaned_data["description"],
                user_id=request.user.id,
                image=file.get_filename(),
            )
            messages.add_message(
                request,
                messages.SUCCESS,
                '<div class="alert alert-success text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
                "<p>Votre demande de critique à été créée avec succès.</p>"
                "</div>",
            )
            return HttpResponseRedirect(reverse('flux_view'))

        else:
            messages.add_message(
                request,
                messages.ERROR,
                '<div class="alert alert-danger text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
                "<p>Veuillez remplir les champs correctement.</p>"
                "<p>Assurez vous que votre image est à la bonne extension : <b>.jpg, .png</b>.</p>"
                "</div>",
            )
            return HttpResponseRedirect(reverse('create_ticket_view'))


class CreateFullReviewView(LoginRequiredMixin, View):
    login_url = settings.LOGIN_URL
    template_name = "dashboard/create_review.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {"rating_range": range(6)})

    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        review_form = CreateReviewForm(request.POST)
        ticket_form = CreateTicketForm(request.POST, request.FILES)
        if review_form.is_valid() and ticket_form.is_valid():
            file = HandleUploadedFile(request.FILES["image"], request.FILES["image"].name)
            Ticket.objects.create(
                title=ticket_form.cleaned_data["title"],
                description=ticket_form.cleaned_data["description"],
                user_id=request.user.id,
                image=file.get_filename(),
            )
            ticket = Ticket.objects.get(
                title=ticket_form.cleaned_data["title"],
                description=ticket_form.cleaned_data["description"],
                user_id=request.user.id,
                image=file.get_filename(),
            )
            Review.objects.create(
                rating=int(review_form.cleaned_data["rating"]),
                headline=review_form.cleaned_data["headline"],
                body=review_form.cleaned_data["body"],
                ticket_id=ticket.id,
                user_id=request.user.id,
            )
            messages.add_message(
                request,
                messages.SUCCESS,
                '<div class="alert alert-success text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
                "<p>Votre critique à été créée avec succès.</p>"
                "</div>",
            )
            return HttpResponseRedirect(reverse('flux_view'))
        else:
            messages.add_message(
                request,
                messages.ERROR,
                '<div class="alert alert-danger text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
                "<p>Veuillez remplir les champs correctement.</p>"
                "<p>Assurez vous que votre image est à la bonne extension : <b>.jpg, .png</b>.</p>"
                "</div>",
            )
            return HttpResponseRedirect(reverse('create_review_view'))


class CreateReviewView(LoginRequiredMixin, View):
    login_url = settings.LOGIN_URL
    template_name = "dashboard/create_answer_review.html"

    def get(self, request,id, *args, **kwargs):
        ticket_id = id
        if isinstance(ticket_id, int) is True and Ticket.objects.filter(id=ticket_id).exists():
            ticket = [ticket for ticket in Ticket.objects.filter(id=ticket_id).values()]
            print(ticket)
            return render(request, self.template_name, {"rating_range": range(6), "ticket": ticket})
        else:
            messages.add_message(
                request,
                messages.ERROR,
                '<div class="alert alert-danger text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
                "<p>Vous essayez d'accèder à un continu qui n'existe pas...</p>"
                "</div>",
            )
            return HttpResponseRedirect(reverse('flux_view'))


    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        review_form = CreateReviewForm(request.POST)
        ticket_form = CreateTicketForm(request.POST, request.FILES)
        if review_form.is_valid() and ticket_form.is_valid():
            file = HandleUploadedFile(request.FILES["image"], request.FILES["image"].name)
            Ticket.objects.create(
                title=ticket_form.cleaned_data["title"],
                description=ticket_form.cleaned_data["description"],
                user_id=request.user.id,
                image=file.get_filename(),
            )
            ticket = Ticket.objects.get(
                title=ticket_form.cleaned_data["title"],
                description=ticket_form.cleaned_data["description"],
                user_id=request.user.id,
                image=file.get_filename(),
            )
            Review.objects.create(
                rating=int(review_form.cleaned_data["rating"]),
                headline=review_form.cleaned_data["headline"],
                body=review_form.cleaned_data["body"],
                ticket_id=ticket.id,
                user_id=request.user.id,
            )
            messages.add_message(
                request,
                messages.SUCCESS,
                '<div class="alert alert-success text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
                "<p>Votre critique à été créée avec succès.</p>"
                "</div>",
            )
            return HttpResponseRedirect(reverse('flux_view'))
        else:
            messages.add_message(
                request,
                messages.ERROR,
                '<div class="alert alert-danger text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
                "<p>Veuillez remplir les champs correctement.</p>"
                "<p>Assurez vous que votre image est à la bonne extension : <b>.jpg, .png</b>.</p>"
                "</div>",
            )
            return HttpResponseRedirect(reverse('create_review_view'))



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
