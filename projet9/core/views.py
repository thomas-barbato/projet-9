from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.views import View
from django.views.generic import RedirectView, UpdateView, DeleteView, TemplateView, CreateView, FormView
from .forms import *
from .models import *
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.urls import reverse, reverse_lazy
import datetime
from .classes.files import HandleUploadedFile
from django.contrib import messages
import json


class JsonableResponseMixin:
    def form_invalid(self, form):
        response = super(JsonableResponseMixin, self).form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        response = super(JsonableResponseMixin, self).form_valid(form)
        if self.request.is_ajax():
            data = {
                'message': "Successfully submitted form data."
            }
            return JsonResponse(data)
        else:
            return response


class CreateUserView(JsonableResponseMixin, FormView):
    template_name: str = "authentication/create_user.html"
    form_class = SignupForm
    success_url = reverse_lazy('login_view')
    success_message = (
                '<div class="alert alert-success text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
                "<p>Votre compte a été créé avec succès.</p>"
                "</div>")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['signup_form'] = SignupForm
        return context

    def form_valid(self, form):
        response = super(JsonableResponseMixin, self).form_valid(form)
        if self.request.is_ajax():
            if form.cleaned_data["password"] == form.cleaned_data["password2"]:
                User.objects.create_user(
                    username=form.cleaned_data["username"],
                    password=form.cleaned_data["password"],
                    is_active=True,
                    is_staff=False,
                    date_joined=datetime.datetime.now(),
                ).save()
                response = {'status': 1}
                messages.add_message(
                    self.request,
                    messages.SUCCESS,
                    self.success_message
                )
                return JsonResponse(response, status=200)
        else:
            return response

    def form_invalid(self, form):
        response = super(JsonableResponseMixin, self).form_invalid(form)
        if self.request.is_ajax():
            response = {"status": 0, "errors": dict(form.errors.items())}
            return JsonResponse(response, status=200)
        return response


class LoginView(TemplateView):
    template_name: str = "authentication/login.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['signin_form'] = SigninForm
        return context

    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
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
            return JsonResponse(response, status=200)
        else:
            response = {"errors": "true"}
            return JsonResponse(response, status=200)


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
        context['rating_range'] = range(5)
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
    error_message=(
        '<div class="alert alert-danger text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
        "<p>Veuillez remplir <b>tous</b> les champs correctement.</p>"
        "<p>Assurez vous que votre image est à la bonne extension : <b>.jpg, .png</b>.</p>"
        "</div>"
    )

    def form_valid(self, form):
        file = HandleUploadedFile(
            file=self.request.FILES["image"], filename=self.request.FILES["image"].name
        )
        file.upload()
        Ticket.objects.create(
            title=self.request.POST.get("title"),
            description=self.request.POST.get("description"),
            user_id=self.request.user.id,
            image=file.get_filename(),
        )
        messages.add_message(
            self.request,
            messages.SUCCESS,
            self.success_message,
        )
        return HttpResponseRedirect(reverse("flux_view"))

    def form_invalid(self, form):
        messages.add_message(
            self.request,
            messages.ERROR,
            self.error_message,
        )
        return HttpResponseRedirect(reverse("create_ticket_view"))


class CreateFullReviewView(LoginRequiredMixin, CreateView):
    login_url = settings.LOGIN_URL
    template_name = "dashboard/create_review.html"
    model = Review
    fields = ["headline", "body", "rating"]
    success_url = reverse_lazy('flux_view')
    success_message = (
                '<div class="alert alert-success text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
                "<p>Votre critique à été créée avec succès.</p>"
                "</div>"
    )
    error_message = (
            '<div class="alert alert-danger text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
            "<p>Veuillez remplir les champs correctement.</p>"
            "<p>Assurez vous que votre image est à la bonne extension : <b>.jpg, .png</b>.</p>"
            "</div>",
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["rating_range"] = range(6)
        return context

    def form_valid(self, form):
        review_form = CreateReviewForm(self.request.POST)
        ticket_form = CreateTicketForm(self.request.POST, self.request.FILES)
        if review_form.is_valid() and ticket_form.is_valid():
            file = HandleUploadedFile(
                file=self.request.FILES["image"], filename=self.request.FILES["image"].name
            )
            file.upload()
            Ticket.objects.create(
                title=ticket_form.cleaned_data.get("title"),
                description=ticket_form.cleaned_data.get("description"),
                user_id=self.request.user.id,
                image=file.get_filename(),
            )
            ticket = Ticket.objects.get(
                title=ticket_form.cleaned_data.get("title"),
                description=ticket_form.cleaned_data.get("description"),
                user_id=self.request.user.id,
                image=file.get_filename(),
            )
            Review.objects.create(
                rating=int(review_form.cleaned_data.get("rating")),
                headline=review_form.cleaned_data.get("headline"),
                body=review_form.cleaned_data.get("body"),
                ticket_id=ticket.id,
                user_id=self.request.user.id,
            )
            messages.add_message(
                self.request,
                messages.SUCCESS,
                self.success_message,
            )
            return HttpResponseRedirect(reverse("flux_view"))

    def form_invalid(self, form):
        messages.add_message(
            self.request,
            messages.ERROR,
            self.error_message,
        )
        return HttpResponseRedirect(reverse("create_review_view"))


class CreateReviewView(LoginRequiredMixin, FormView):
    login_url = settings.LOGIN_URL
    template_name = "dashboard/create_answer_review.html"
    form_class = CreateReviewForm
    fields = ["headline", "body", "rating"]
    success_message = (
        '<div class="alert alert-success text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
        "<p>Votre critique à été créée avec succès.</p>"
        "</div>"
    )
    error_message= (
        '<div class="alert alert-danger text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
        "<p>Veuillez remplir les champs correctement.</p>"
        "</div>"
    )
    error_message2 = (
        '<div class="alert alert-danger text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
        "<p>le ticket pour lequel vous tentez de faire une review n'existe pas.</p>"
        "</div>"

    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ticket_id = self.kwargs['id']
        ticket = [
            ticket
            for ticket in Ticket.objects.select_related(
                "user", "ticket", "ticket__user_id__username", "user__username", "user_id__username").filter(
                id=ticket_id).values(
                "id",
                "title",
                "description",
                "image",
                "time_created",
                "user_id",
                "user_id__username"
            )
        ]
        context["rating_range"] = range(6)
        context["ticket"] = ticket
        return context

    def form_valid(self, form):
        ticket_id = self.kwargs['id']
        if (
                isinstance(ticket_id, int) is True
                and Ticket.objects.filter(id=ticket_id).exists()
        ):
            Review.objects.create(
                rating=int(self.request.POST.get("rating")),
                headline=self.request.POST.get("headline"),
                body=self.request.POST.get("body"),
                ticket_id=ticket_id,
                user_id=self.request.user.id,
            )
            messages.add_message(
                self.request,
                messages.SUCCESS,
                self.success_message,
            )
            return HttpResponseRedirect(reverse("flux_view"))
        else:
            messages.add_message(
                self.request,
                messages.ERROR,
                self.error_message2,
            )
            return HttpResponseRedirect(reverse("flux_view"))

    def form_invalid(self, form):
        messages.add_message(
            self.request,
            messages.ERROR,
            self.error_message,
        )
        return HttpResponseRedirect(reverse("create_review_view"))


class DislayPostsView(LoginRequiredMixin, TemplateView):
    login_url = settings.LOGIN_URL
    template_name = "dashboard/posts.html"
    empty_content_message = (
        '<div class="alert alert-info text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
        "<p>Vous n'avez encore rien publié</p>"
        "</div>"
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query_review = [
            result
            for result in Review.objects.select_related(
                "user", "ticket", "ticket__user_id", "user__username"
            ).filter(user_id=self.request.user.id)
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
                self.request,
                messages.INFO,
                self.empty_content_message,
            )
        else:
            context["posts"] = query_review
            context["rating_range"] = range(5)
        return context


class UpdatePost(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    login_url = settings.LOGIN_URL
    model = Review
    fields = [
            "headline",
            "body",
            "rating"]
    success_message = (
                '<div class="alert alert-success text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
                "<p>Critique modifiée avec succès.</p>"
                "</div>")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["rating_range"] = range(5)
        context["body_content"] = Review.objects.filter(id=self.kwargs['pk'], user_id=self.request.user.id).values()[0]['body']
        return context


class DeletePost(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Review
    success_url = reverse_lazy('posts_view')
    success_message = (
        '<div class="alert alert-success text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
        "<p>Critique supprimée avec succès.</p>"
        "</div>"
    )

    def delete(self, request, *args, **kwargs):
        data_to_return = super(DeletePost, self).delete(request, *args, **kwargs)
        messages.success(self.request, self.success_message)
        return data_to_return


class DisplaySuscribeView(LoginRequiredMixin, TemplateView):
    login_url = settings.LOGIN_URL
    template_name: str = "dashboard/suscribe.html"
    success_url = reverse_lazy('suscribe_view')
    model = UserFollows
    form_class = FollowUserForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_follow_list = UserFollows.objects.filter(user_id=self.request.user.id).select_related('user', 'user__id', 'user__username').values('id','followed_user_id__username')
        followed_by_list = UserFollows.objects.filter(followed_user_id=self.request.user.id).select_related('user', 'user__id', 'user__username').values('user_id__username')
        context["suscribe"] = user_follow_list
        context["followed_by"] = followed_by_list
        return context

    def post(self, request, *args, **kwargs):
        username: str = self.request.POST.get('id_username')
        followed_user = User.objects.filter(username=username)
        if followed_user.exists():
            follower_id = followed_user.values('id', 'username')[0]['id']
            if not UserFollows.objects.filter(user_id=self.request.user.id, followed_user=follower_id).exists():
                UserFollows.objects.create(
                    user_id=self.request.user.id,
                    followed_user=User(id=follower_id)
                )
                messages.add_message(
                    self.request,
                    messages.SUCCESS,
                    '<div class="alert alert-success text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
                    f'<p>Vous suivez maintenant <b>{username}</b>.</p>'
                    '</div>',
                )
            else:
                messages.add_message(
                    self.request,
                    messages.INFO,
                    '<div class="alert alert-info text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
                    "<p>Vous suivez déjà cet utilisateur.</p>"
                    "</div>",
                )
        else:
            messages.add_message(
                self.request,
                messages.ERROR,
                '<div class="alert alert-info text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
                '<p>l\'utilisateur que vous recherchez n\'existe pas.</p>'
                '</div>',
            )
        return HttpResponseRedirect(reverse('suscribe_view'))


class UnfollowUser(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    login_url = settings.LOGIN_URL
    template_name: str = "dashboard/suscribe.html"
    success_url = reverse_lazy('suscribe_view')
    model = UserFollows
    success_message = (
        '<div class="alert alert-success text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
        "<p>Vous ne suivez plus cet utilisateur.</p>"
        "</div>"
    )

    def delete(self, request, *args, **kwargs):
        data_to_return = super(UnfollowUser, self).delete(request, *args, **kwargs)
        messages.success(self.request, self.success_message)
        return data_to_return


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
