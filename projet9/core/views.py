from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, redirect, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.views import View
from django.contrib.sessions.models import Session
from django.views.generic import RedirectView, UpdateView, DeleteView, DetailView, ListView, TemplateView, CreateView, FormView
from django.views.generic.edit import FormMixin

from .forms import *
from .models import *
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse, reverse_lazy
import datetime
import json
from .classes.files import HandleUploadedFile
from django.contrib import messages
from django.forms.models import model_to_dict
from django.http import Http404


class JsonableResponseMixin:
    """
    Mixin to add JSON support to a form.
    Must be used with an object-based FormView (e.g. CreateView)
    """
    def form_invalid(self, form):
        response = super().form_invalid(form)
        if self.request.accepts('text/html'):
            return response
        else:
            return JsonResponse(form.errors, status=400)

    def form_valid(self, form):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        response = super().form_valid(form)
        if self.request.accepts('text/html'):
            return response
        else:
            data = {
                'pk': self.object.pk,
            }
            return JsonResponse(data)


class CreateUserView(CreateView):
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


class SignupSuccessView(RedirectView):
    template_name = "dashboard/flux.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['signin_form'] = SigninForm
        return context


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


class FluxView(LoginRequiredMixin, SuccessMessageMixin, TemplateView):
    login_url = settings.LOGIN_URL
    template_name = "dashboard/posts.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query_review = [
            result
            for result in Review.objects.select_related(
                "user", "ticket", "ticket__user_id", "user__username"
            )
            .values(
                "headline",
                "body",
                "rating",
                "time_created",
                "ticket_id",
                "user_id",
                "user__username",
                "ticket__image",
                "ticket__title",
                "ticket__user_id__username",
            )
            .order_by("-time_created")
        ]

        review = [dict(item, is_review=True) for item in query_review]

        query_ticket = [
            result
            for result in Ticket.objects.select_related("user")
            .values(
                "id",
                "title",
                "description",
                "image",
                "user_id",
                "user__username",
                "time_created",
            )
            .order_by("-time_created")
        ]

        ticket = [dict(item, is_ticket=True) for item in query_ticket]

        result = []
        ticket.extend(review)
        for item in ticket:
            if item not in result:
                result.append(item)

        result = sorted(result, key=lambda d: d["time_created"], reverse=True)
        context['posts'] = result
        return context

class CreateTicketView(LoginRequiredMixin, JsonableResponseMixin, CreateView):
    login_url = settings.LOGIN_URL
    template_name = "dashboard/create_ticket.html"
    model = Ticket
    fields = ["title", "description", "image"]
    success_url = reverse_lazy('flux_view')
    success_message = (
                '<div class="alert alert-success text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
                "<p>Votre demande de critique à été créée avec succès.</p>"
                "</div>")

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            file = HandleUploadedFile(
                file=request.FILES["image"], filename=request.FILES["image"].name
            )
            file.upload()
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
            return HttpResponseRedirect(reverse("flux_view"))

        else:
            messages.add_message(
                request,
                messages.ERROR,
                '<div class="alert alert-danger text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
                "<p>Veuillez remplir <b>tous</b> les champs correctement.</p>"
                "<p>Assurez vous que votre image est à la bonne extension : <b>.jpg, .png</b>.</p>"
                "</div>",
            )
            return HttpResponseRedirect(reverse("create_ticket_view"))

"""
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            file = HandleUploadedFile(
                file=request.FILES["image"], filename=request.FILES["image"].name
            )
            file.upload()
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
            return HttpResponseRedirect(reverse("flux_view"))

        else:
            messages.add_message(
                request,
                messages.ERROR,
                '<div class="alert alert-danger text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
                "<p>Veuillez remplir <b>tous</b> les champs correctement.</p>"
                "<p>Assurez vous que votre image est à la bonne extension : <b>.jpg, .png</b>.</p>"
                "</div>",
            )
            return HttpResponseRedirect(reverse("create_ticket_view"))
            """


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
            file = HandleUploadedFile(
                file=request.FILES["image"], filename=request.FILES["image"].name
            )
            file.upload()
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
            return HttpResponseRedirect(reverse("flux_view"))
        else:
            messages.add_message(
                request,
                messages.ERROR,
                '<div class="alert alert-danger text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
                "<p>Veuillez remplir les champs correctement.</p>"
                "<p>Assurez vous que votre image est à la bonne extension : <b>.jpg, .png</b>.</p>"
                "</div>",
            )
            return HttpResponseRedirect(reverse("create_review_view"))


class CreateReviewView(LoginRequiredMixin, View):
    login_url = settings.LOGIN_URL
    template_name = "dashboard/create_answer_review.html"

    def get(self, request, id, *args, **kwargs):
        ticket_id = id
        if (
            isinstance(ticket_id, int) is True
            and Ticket.objects.filter(id=ticket_id).exists()
        ):
            ticket = [
                ticket
                for ticket in Ticket.objects.select_related(
                "user", "ticket", "ticket__user_id__username", "user__username", "user_id__username").filter(id=ticket_id).values(
                    "id",
                    "title",
                    "description",
                    "image",
                    "time_created",
                    "user_id",
                    "user_id__username"
                )
            ]
            print(ticket)
            return render(
                request,
                self.template_name,
                {"rating_range": range(6), "ticket": ticket},
            )
        else:
            messages.add_message(
                request,
                messages.ERROR,
                '<div class="alert alert-danger text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
                "<p>Vous essayez d'accèder à un continu qui n'existe pas...</p>"
                "</div>",
            )
            return HttpResponseRedirect(reverse("flux_view"))

    @method_decorator(csrf_protect)
    def post(self, request, id, *args, **kwargs):
        ticket_id = id
        if (
            isinstance(ticket_id, int) is True
            and Ticket.objects.filter(id=ticket_id).exists()
        ):
            review_form = CreateReviewForm(request.POST)
            if review_form.is_valid():
                Review.objects.create(
                    rating=int(review_form.cleaned_data["rating"]),
                    headline=review_form.cleaned_data["headline"],
                    body=review_form.cleaned_data["body"],
                    ticket_id=ticket_id,
                    user_id=request.user.id,
                )
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    '<div class="alert alert-success text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
                    "<p>Votre critique à été créée avec succès.</p>"
                    "</div>",
                )
                return HttpResponseRedirect(reverse("flux_view"))
            else:
                messages.add_message(
                    request,
                    messages.ERROR,
                    '<div class="alert alert-danger text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
                    "<p>Veuillez remplir les champs correctement.</p>"
                    "</div>",
                )
                return HttpResponseRedirect(reverse("create_review_view"))
        else:
            messages.add_message(
                request,
                messages.ERROR,
                '<div class="alert alert-danger text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
                "<p>Vous essayez d'accèder à un continu qui n'existe pas...</p>"
                "</div>",
            )
            return HttpResponseRedirect(reverse("flux_view"))


class DislayPostsView(LoginRequiredMixin, View):
    login_url = settings.LOGIN_URL
    template_name = "dashboard/posts.html"
    update_template_name = "dashboard/update_post.html"

    def get(self, request, *args, **kwargs):
        query_review = [
            result
            for result in Review.objects.select_related(
                "user", "ticket", "ticket__user_id", "user__username"
            ).filter(user_id=request.user.id)
            .values(
                "id",
                "headline",
                "body",
                "rating",
                "time_created",
                "ticket_id",
                "user_id",
                "user__username",
                "ticket__image",
                "ticket__title",
                "ticket__user_id__username",
            )
            .order_by("-time_created")
        ]

        if len(query_review) == 0:
            messages.add_message(
                request,
                messages.INFO,
                '<div class="alert alert-info text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
                "<p>Vous n'avez encore rien publié</p>"
                "</div>",
            )

        return render(
            request,
            self.template_name,
            {"posts": query_review, "star_range": range(5)},
        )

    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        review_id = int(request.POST.get('post_id'))
        if Review.objects.filter(user_id=request.user.id, id=review_id).exists():
            review = Review.objects.filter(user_id=request.user.id, id=int(request.POST.get('post_id')))
            review.update(
                headline=request.POST.get('headline'),
                body=request.POST.get('body'),
                rating=request.POST.get('rating')
            )
            messages.add_message(
                request,
                messages.SUCCESS,
                '<div class="alert alert-success text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
                "<p>Critique modifiée avec succès.</p>"
                "</div>",
            )
            return HttpResponseRedirect(reverse("posts_view"))
        else:
            messages.add_message(
                request,
                messages.ERROR,
                '<div class="alert alert-danger text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
                "<p>Vous essayez de modifier un continu qui n'existe pas...</p>"
                "</div>",
            )
            return HttpResponseRedirect(reverse("posts_view"))


    @staticmethod
    def delete(request):
        post_id = int(request.POST.get('post_id'))
        if Review.objects.filter(user_id=request.user.id, id=post_id).exists():
            review = Review.objects.select_related('ticket').filter(user_id=request.user.id, id=post_id)
            img_name = review.values("ticket__image")[0]['ticket__image']
            HandleUploadedFile(
                filename=img_name
            ).delete()
            review.delete()
            messages.add_message(
                request,
                messages.SUCCESS,
                '<div class="alert alert-success text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
                "<p>Votre poste à correctement été supprimé.</p>"
                "</div>",
            )
            return HttpResponseRedirect(reverse("posts_view"))
        else:
            messages.add_message(
                request,
                messages.ERROR,
                '<div class="alert alert-danger text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
                "<p>Vous essayez de supprimer à un continu qui n'existe pas...</p>"
                "</div>",
            )
            return HttpResponseRedirect(reverse("posts_view"))


class UpdatePost(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Review
    fields = [
            "headline",
            "body",
            "rating"]
    success_message = (
                '<div class="alert alert-success text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
                "<p>Critique modifiée avec succès.</p>"
                "</div>")


class DeletePost(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Review
    success_url = reverse_lazy('posts_view')
    success_message = (
                '<div class="alert alert-success text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
                "<p>Critique modifiée avec succès.</p>"
                "</div>")

    def delete(self, request, *args, **kwargs):
        data_to_return = super(DeletePost, self).delete(request, *args, **kwargs)
        messages.success(self.request, self.success_message)
        return data_to_return



class DisplaySuscribeView(LoginRequiredMixin, View):
    template_name: str = "dashboard/suscribe.html"

    @method_decorator(csrf_exempt)
    def get(self, request, *args, **kwargs):
        user_follow_list = UserFollows.objects.filter(user_id=request.user.id).select_related('user', 'user__id', 'user__username').values('followed_user_id__username')
        followed_by_list = UserFollows.objects.filter(followed_user_id=request.user.id).select_related('user', 'user__id', 'user__username').values('user_id__username')
        return render(request, self.template_name, {"suscribe": user_follow_list, "followed_by": followed_by_list})

    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        username: str = request.POST.get('username')
        response: dict = {}
        if username:
            followed_user = User.objects.filter(username=username)
            if followed_user.exists():
                follower_id = followed_user.values('id', 'username')[0]['id']
                if not UserFollows.objects.filter(user_id=request.user.id, followed_user=follower_id).exists():
                    UserFollows.objects.create(
                        user_id=request.user.id,
                        followed_user=User(id=follower_id)
                    )
                    response = {
                        "status": 1,
                        "error":
                            '<div class="alert alert-success text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
                            f"<p>Vous suivez maintenant {username}.</p>"
                            "</div>",
                        "username": f"{username}"
                    }
                else:
                    response = {
                        "status": 0,
                        "error":
                            '<div class="alert alert-danger text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
                            "<p>Vous suivez déjà cet utilisateur.</p>"
                            "</div>"
                    }
            else:
                response = {
                    "status": 0,
                    "error":
                        '<div class="alert alert-danger text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
                        "<p>l'utilisateur que vous recherchez n'existe pas.</p>"
                        "</div>"
                }

        else:
            response = {
                "status": 0,
                "error":
                '<div class="alert alert-danger text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
                "<p>Vous devez entrer un nom d'utilisateur...</p>"
                "</div>"
            }
        return JsonResponse(response)

    @method_decorator(csrf_protect)
    def unfollow(self, request, *args, **kwargs):
        print(request.POST)








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
