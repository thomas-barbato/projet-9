""" imports """
import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Value
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    FormView,
    TemplateView,
    UpdateView,
)
from django.views.generic.list import ListView

from .forms import (
    CreateReviewForm,
    CreateTicketForm,
    FollowUserForm,
    SigninForm,
    SignupForm,
)
from .helper.files import HandleUploadedFile
from .models import Review, Ticket, UserFollows


class JsonableResponseMixin:
    """
    Mixin to add JSON support to a form.
    Must be used with an object-based FormView (e.g. CreateView)
    """

    def form_invalid(self, form):
        """docstring"""
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        return super().form_invalid(form)

    def form_valid(self, form):
        """docstring"""
        if self.request.is_ajax():
            data = {"message": "Successfully submitted form data."}
            return JsonResponse(data)
        return super().form_valid(form)


class CreateUserView(JsonableResponseMixin, FormView):
    """Allow user account creation
    :Ancestor FormView: View which display form.
        return validation error and redirect to success url
    :Ancestor JsonableResponseMixin:
        Check if request is ajax
    :return:
        "authentication/create_user.html"
    :rtype: template
    """

    template_name: str = "authentication/create_user.html"
    form_class = SignupForm
    success_url = reverse_lazy("login_view")
    success_message = (
        '<div class="alert alert-success text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
        "<p>Votre compte a été créé avec succès.</p>"
        "</div>"
    )

    def form_valid(self, form):
        """Override form_valid to create user and add 'is_active', 'date_joined', 'is_staff', and custom success msg
        :param form: SignupForm, used to create user.
        :type form: form
        :return: JsonResponse with response message and status 200 if request is ajax type
         else return JsonableResponseMixin form_valid
        :rtype: Ajax
        """
        if self.request.is_ajax():
            if form.cleaned_data["password"] == form.cleaned_data["password2"]:
                User.objects.create_user(
                    username=form.cleaned_data["username"],
                    password=form.cleaned_data["password"],
                    is_active=True,
                    is_staff=False,
                    date_joined=datetime.datetime.now(),
                ).save()
                response = {"status": 1}
                messages.add_message(
                    self.request, messages.SUCCESS, self.success_message
                )
                return JsonResponse(response, status=200)
        return super(JsonableResponseMixin, self).form_valid(form)

    def form_invalid(self, form):
        """Override form_invalid to return custom error message
        :param form: SignupForm, used to create user.
        :type form: form
        :return: JsonResponse with response message, error dict and status 200 if request is ajax type
         else return JsonableResponseMixin form_valid
        :rtype: Ajax
        """
        response = super(JsonableResponseMixin, self).form_invalid(form)
        if self.request.is_ajax():
            response = {"status": 0, "errors": dict(form.errors.items())}
        return JsonResponse(response, status=200)


class LoginAjaxView(LoginView):
    """Check user, login and redirect to flux_view
    :Ancestor: LoginView
        Display login form and handle login action
    :return: "authentication/login.html"
    :rtype: Template
    """

    redirect_authenticated_user = True

    def get_success_url(self):
        """success url set to redirect after login in
        :Argument: self
        :type self : /
        :return: redirection to flux_view
        :rtype: str
        """
        return reverse_lazy("flux_view")

    def get_context_data(self, **kwargs):
        """Override get_context_data to return form
        :param kwargs: kwargs.
        :return: context
        :rtype: list
        """
        context = super().get_context_data(**kwargs)
        context["signin_form"] = SigninForm
        return context

    def form_valid(self, form):
        """Override form_valid, called to log user, return ajax
        :param form: form
            return validation error and redirect to success url
        :return:
            ajax response (status)
        :rtype: Json
        """
        user = authenticate(
            self.request,
            username=self.request.POST.get("username"),
            password=self.request.POST.get("password"),
        )
        if user is not None:
            login(self.request, user)
            response = {"status": 1}
            messages.add_message(
                self.request,
                messages.SUCCESS,
                '<div class="alert alert-success text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
                "<p>Vous êtes maintenant connecté.</p>"
                "</div>",
            )
            return JsonResponse(response, status=200)

    def form_invalid(self, form):
        """Override form_invalid, return error
        :param form: form
            return validation error and redirect to success url
        :Ancestor JsonableResponseMixin:
        :return:
            ajax response (status)
        :rtype: Json
        """
        response = {"errors": "true"}
        return JsonResponse(response, status=200)


class FluxView(LoginRequiredMixin, TemplateView):
    """Display flux view template
    :Ancestors: LoginRequiredMixin
        Allow to access flux_view if user is authenticated
    :Ancestor SuccessMessageMixin:
        Add a success message on successful from submission
    :Ancestor TemplateView:
        Render a template
    :return:"dashboard/flux.html"
    :rtype: Template
    """

    login_url = settings.LOGIN_URL
    template_name = "dashboard/posts.html"

    def get_context_data(self, **kwargs):
        """Override get_context_data to return form
        :param kwargs: kwargs.
        :return: context
        :rtype: list
        """
        context = super().get_context_data(**kwargs)
        review = list(
            # TODO : ANNOTATION
            Review.objects.select_related(
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
            .annotate(is_review=Value(True))
            .order_by("-time_created")
        )

        ticket = list(
            Ticket.objects.select_related("user")
            .values(
                "id",
                "title",
                "description",
                "image",
                "user_id",
                "user__username",
                "time_created",
            )
            .annotate(is_ticket=Value(True))
            .order_by("-time_created")
        )

        result = []
        ticket.extend(review)
        for item in ticket:
            if item not in result:
                result.append(item)

        result = sorted(result, key=lambda d: d["time_created"], reverse=True)
        context["posts"] = result
        context["rating_range"] = range(5)
        return context


class CreateTicketView(LoginRequiredMixin, CreateView):
    """Display create new ticket template
    :Ancestors: LoginRequiredMixin
        Allow to create ticket if user is authenticated
    :Ancestor CreateView:
        View for creating new object, with a response rendered by template
    :return:
        "dashboard/create_ticket.html"
    :rtype: template
    """

    login_url = settings.LOGIN_URL
    template_name = "dashboard/create_ticket.html"
    model = Ticket
    form_class = CreateTicketForm
    success_url = reverse_lazy("flux_view")
    success_message = (
        '<div class="alert alert-success text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
        "<p>Votre demande de critique à été créée avec succès.</p>"
        "</div>"
    )
    error_message = (
        '<div class="alert alert-danger text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
        "<p>Veuillez remplir <b>tous</b> les champs correctement.</p>"
        "<p>Assurez vous que votre image est à la bonne extension : <b>.jpg, .png</b>.</p>"
        "</div>"
    )

    def form_valid(self, form):
        """Override form_valid, save ticket and return himself
        :param form: form
            return validation error and redirect to success url
        :return:
            himself
        :rtype: form_valid
        """
        form.save(user=self.request.user, file=self.request.FILES["image"])

        messages.add_message(
            self.request,
            messages.SUCCESS,
            self.success_message,
        )
        return HttpResponseRedirect(reverse("flux_view"))

    def form_invalid(self, form):
        """Override form_invalid, add error message
        :param form: form
            return validation error and redirect to success url
        :return:
            himself
        :rtype: form_invalid
        """
        messages.add_message(
            self.request,
            messages.ERROR,
            self.error_message,
        )
        return super().form_invalid(form)


class CreateFullReviewView(LoginRequiredMixin,  CreateView):
    """Display create new full review (ticket + review)
    :Ancestors: LoginRequiredMixin
        Allow to create ticket if user is authenticated
    :Ancestor CreateView:
        View for creating new object, with a response rendered by template
    :Ancestor SuccessMessageMixin
        Add a success message on successful from submission
    :return:
        "dashboard/create_review.html"
    :rtype: template
    """

    login_url = settings.LOGIN_URL
    template_name = "dashboard/create_review.html"
    model = Review
    form_class = CreateReviewForm
    success_url = reverse_lazy("flux_view")
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
        """Override get_context_data to return form
        :param kwargs: kwargs.
        :return: context
        :rtype: list
        """
        context = super().get_context_data(**kwargs)
        context["rating_range"] = range(6)
        return context

    def form_valid(self, form):
        """Override form_valid, save review + ticket and return himself
        :param form: form
            return validation error and redirect to success url
        :return:
            himself
        :rtype: form_valid
        """
        ticket_form = CreateTicketForm(self.request.POST, self.request.FILES)
        if ticket_form.is_valid():
            ticket_form.save(user=self.request.user, file=self.request.FILES["image"])
            form.save(user=self.request.user, ticket_id=ticket_form.instance.id)
            messages.add_message(
                self.request,
                messages.SUCCESS,
                self.success_message,
            )
        return HttpResponseRedirect(reverse("flux_view"))

    def form_invalid(self, form):
        """Override form_invalid, display error message
        :param form: form
            return validation
        :return:
            himself
        :rtype: form_invalid
        """
        messages.add_message(
            self.request,
            messages.ERROR,
            self.error_message,
        )
        return HttpResponseRedirect(reverse("create_review_view"))


class CreateReviewView(LoginRequiredMixin, CreateView):
    """Display create new review (review only)
    :Ancestors: LoginRequiredMixin
        Allow to create ticket if user is authenticated
    :Ancestor FormView:
        A view for displaying a form and rendering a template response
    :return:
        "dashboard/create_review.html"
    :rtype: template
    """

    login_url = settings.LOGIN_URL
    template_name = "dashboard/create_answer_review.html"
    model = Review
    form_class = CreateReviewForm
    success_message = (
        '<div class="alert alert-success text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
        "<p>Votre critique à été créée avec succès.</p>"
        "</div>"
    )
    error_message = (
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
        """Override get_context_data to return form
        :param kwargs: kwargs.
        :return: context
        :rtype: list
        """
        context = super().get_context_data(**kwargs)
        ticket_id = self.kwargs["id"]
        ticket = list(
            Ticket.objects.select_related(
                "user",
                "ticket",
                "ticket__user_id__username",
                "user__username",
                "user_id__username",
            )
            .filter(id=ticket_id)
            .values(
                "id",
                "title",
                "description",
                "image",
                "time_created",
                "user_id",
                "user_id__username",
            )
        )
        context["rating_range"] = range(6)
        context["ticket"] = ticket
        return context

    def form_valid(self, form):
        """Override form_valid, create Review and add message
        :param form: form
            return validation error and redirect to success url
        :return:
            himself
        :rtype: form_valid
        """
        ticket_id = self.kwargs["id"]
        if (
            isinstance(ticket_id, int) is True
            and Ticket.objects.filter(id=ticket_id).exists()
        ):

            form.save(user=self.request.user, ticket_id=ticket_id)
            messages.add_message(
                self.request,
                messages.SUCCESS,
                self.success_message,
            )
        else:
            messages.add_message(
                self.request,
                messages.ERROR,
                self.error_message2,
            )
        return HttpResponseRedirect(reverse("flux_view"))

    def form_invalid(self, form):
        """Override form_invalid, display error message
        :param form: form
            return validation
        :return:
            himself
        :rtype: form_invalid
        """
        messages.add_message(
            self.request,
            messages.ERROR,
            self.error_message,
        )
        return HttpResponseRedirect(reverse("create_review_view"))


class DisplayPostsView(LoginRequiredMixin, TemplateView):
    """Display post view template (ordered by created time)
    :Ancestors: LoginRequiredMixin
        Allow to access posts_view if user is authenticated
    :Ancestor TemplateView:
        Render a template. Pass keyword argument from URLconf to the context
    :return:
        "dashboard/posts.html"
    :rtype: Template
    """

    login_url = settings.LOGIN_URL
    template_name = "dashboard/posts.html"
    empty_content_message = (
        '<div class="alert alert-info text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
        "<p>Vous n'avez encore rien publié</p>"
        "</div>"
    )

    def get_context_data(self, **kwargs):
        """Override get_context_data to return form
        :param kwargs: kwargs.
        :return: context
        :rtype: list
        """
        context = super().get_context_data(**kwargs)
        query_review = list(
            Review.objects.select_related(
                "user", "ticket", "ticket__user_id", "user__username"
            )
            .filter(user_id=self.request.user.id)
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
            .annotate(is_review=Value(True))
            .order_by("-time_created")
        )

        query_ticket = list(
            Ticket.objects.select_related("user")
            .filter(user_id=self.request.user.id)
            .values(
                "id",
                "title",
                "description",
                "image",
                "user_id",
                "user__username",
                "time_created",
            )
            .annotate(is_ticket=Value(True))
            .order_by("-time_created")
        )

        result = []
        query_ticket.extend(query_review)
        for item in query_ticket:
            if item not in result:
                result.append(item)

        if len(result) == 0:
            messages.add_message(
                self.request,
                messages.INFO,
                self.empty_content_message,
            )
        else:
            context["posts"] = result
            context["rating_range"] = range(5)
        return context


class UpdatePost(LoginRequiredMixin, UpdateView):
    """Display update_posts.html template and save edited values.
    :Ancestors: LoginRequiredMixin
        Allow to access update_posts if user is authenticated
    :Ancestor UpdateView:
        View for updating an object, with a response rendered by template
    :return:
        "dashboard/update_posts.html"
    :rtype: Template
    """

    login_url = settings.LOGIN_URL
    model = Review
    fields = ["headline", "body", "rating"]
    success_message = (
        '<div class="alert alert-success text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
        "<p>Critique modifiée avec succès.</p>"
        "</div>"
    )

    def get_context_data(self, **kwargs):
        """Override get_context_data to return form
        :param kwargs: kwargs.
        :return: context
        :rtype: list
        """
        context = super().get_context_data(**kwargs)
        context["rating_range"] = range(5)
        context["body_content"] = Review.objects.filter(
            id=self.kwargs["pk"], user_id=self.request.user.id
        ).values()[0]["body"]
        return context


class UpdateTicket(LoginRequiredMixin, UpdateView):
    """Display update_ticket.html template and save edited values.
    :Ancestors: LoginRequiredMixin
        Allow to access update_posts if user is authenticated
    :Ancestor UpdateView:
        View for updating an object, with a response rendered by template
    :return:
        "dashboard/update_ticket.html"
    :rtype: Template
    """

    login_url = settings.LOGIN_URL
    model = Ticket
    fields = ["title", "description", "image"]
    success_message = (
        '<div class="alert alert-success text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
        "<p>Ticket modifié avec succès.</p>"
        "</div>"
    )

    def get_context_data(self, **kwargs):
        """Override get_context_data to return form
        :param kwargs: kwargs.
        :return: context
        :rtype: list
        """
        context = super().get_context_data(**kwargs)
        context["description_content"] = Ticket.objects.filter(
            id=self.kwargs["pk"]
        ).values()[0]["description"]
        return context

    def form_valid(self, form):
        """Override form_valid, update ticket + and return himself
        :param form: form
            return validation error and redirect to success url
        :return:
            himself
        :rtype: form_valid
        """
        ticket_id = self.kwargs["pk"]
        if (
            isinstance(ticket_id, int) is True
            and Ticket.objects.filter(id=ticket_id).exists()
        ):

            file = HandleUploadedFile(
                file=self.request.FILES["image"],
                filename=self.request.FILES["image"].name,
            )
            file.upload()
            ticket = Ticket.objects.get(id=ticket_id)
            HandleUploadedFile().delete_standalone_img(filename=ticket.image)
            ticket.title = form.cleaned_data.get("title")
            ticket.description = form.cleaned_data.get("description")
            ticket.user_id = self.request.user.id
            ticket.image = file.get_filename()
            ticket.save()
            messages.add_message(self.request, messages.SUCCESS, self.success_message)
        return HttpResponseRedirect(reverse("posts_view"))


class DeletePost(LoginRequiredMixin, DeleteView):
    """Delete post.
    :Ancestors: LoginRequiredMixin
        Allow to access update_posts if user is authenticated
    :Ancestors: SuccessMessageMixin
        Add a success message on successful form submission
    :Ancestor DeleteView:
        View for deleting an object retrieved with self.get_object() with a response rendered by a template
    :return:
        "dashboard/posts_view.html"
    :rtype: Template
    """

    model = Review
    success_url = reverse_lazy("posts_view")
    success_message = (
        '<div class="alert alert-success text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
        "<p>Critique supprimée avec succès.</p>"
        "</div>"
    )

    def delete(self, request, *args, **kwargs):
        """Override delete and display success message
        :param request: request
            Django uses request and response objects to pass state through the system
        :return:
            himself
        :rtype: form_valid
        """
        ticket_image = (
            Review.objects.select_related("ticket")
            .filter(user_id=self.request.user.id)
            .values("ticket__image")[0]["ticket__image"]
        )
        HandleUploadedFile.delete_standalone_img(filename=ticket_image)
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class DeleteTicket(LoginRequiredMixin, DeleteView):
    """Delete ticket.
    :Ancestors: LoginRequiredMixin
        Allow to access update_posts if user is authenticated
    :Ancestors: SuccessMessageMixin
        Add a success message on successful form submission
    :Ancestor DeleteView:
        View for deleting an object retrieved with self.get_object() with a response rendered by a template
    :return:
        "dashboard/posts_view.html"
    :rtype: Template
    """

    model = Ticket
    success_url = reverse_lazy("posts_view")
    success_message = (
        '<div class="alert alert-success text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
        "<p>Ticket supprimé avec succès.</p>"
        "</div>"
    )

    def delete(self, request, *args, **kwargs):
        """Override delete and display success message
        :param request: request
            Django uses request and response objects to pass state through the system
        :return:
            himself
        :rtype: form_valid
        """
        file = Ticket.objects.get(id=self.kwargs["pk"])
        HandleUploadedFile.delete_standalone_img(filename=file.image)
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class DisplaySuscribeView(LoginRequiredMixin, ListView):
    """Delete ticket.
    :Ancestors: LoginRequiredMixin
        Allow to access update_posts if user is authenticated
    :Ancestor ListView:
        Render some list of objects, set by "self.object" or "self.queryset"
        `self.queryset` can actually be any iterable of items, not just a queryset.
    :return:
        "dashboard/posts_view.html"
    :rtype: Template
    """

    login_url = settings.LOGIN_URL
    template_name: str = "dashboard/suscribe.html"
    success_url = reverse_lazy("suscribe_view")
    model = UserFollows
    form_class = FollowUserForm

    def get_context_data(self, **kwargs):
        """Override get_context_data to return form
        :param kwargs: kwargs.
        :return: context
        :rtype: list
        """
        context = super().get_context_data(**kwargs)
        user_follow_list = (
            UserFollows.objects.filter(user_id=self.request.user.id)
            .select_related("user", "user__id", "user__username")
            .values("id", "followed_user_id__username")
        )
        followed_by_list = (
            UserFollows.objects.filter(followed_user_id=self.request.user.id)
            .select_related("user", "user__id", "user__username")
            .values("user_id__username")
        )
        context["suscribe"] = user_follow_list
        context["followed_by"] = followed_by_list
        return context

    def post(self, *args, **kwargs):  # pylint: disable=unused-argument
        """Override post to add UserFollows, return template and messages
        :param kwargs: kwargs.
        :return: template "dashboard/suscribe.html"
        :rtype: Template
        """
        username: str = self.request.POST.get("id_username")
        followed_user = User.objects.filter(username=username)
        if followed_user.exists():
            follower_id = followed_user.values("id", "username")[0]["id"]
            if not UserFollows.objects.filter(
                user_id=self.request.user.id, followed_user=follower_id
            ).exists():
                UserFollows.objects.create(
                    user_id=self.request.user.id,
                    followed_user=User(id=follower_id),
                )
                messages.add_message(
                    self.request,
                    messages.SUCCESS,
                    '<div class="alert alert-success text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
                    f"<p>Vous suivez maintenant <b>{username}</b>.</p>"
                    "</div>",
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
                "<p>l'utilisateur que vous recherchez n'existe pas.</p>"
                "</div>",
            )
        return HttpResponseRedirect(reverse("suscribe_view"))


class UnfollowUser(LoginRequiredMixin, DeleteView):
    """Unfollow User ; delete link between 2 users.
    :Ancestors: LoginRequiredMixin
        Allow to access update_posts if user is authenticated
    :Ancestors: SuccessMessageMixin
        Add a success message on successful form submission
    :Ancestor DeleteView:
        View for deleting an object retrieved with self.get_object() with a response rendered by a template
    :return:
        "dashboard/suscribe.html"
    :rtype: Template
    """

    login_url = settings.LOGIN_URL
    template_name: str = "dashboard/suscribe.html"
    success_url = reverse_lazy("suscribe_view")
    model = UserFollows
    success_message = (
        '<div class="alert alert-success text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
        "<p>Vous ne suivez plus cet utilisateur.</p>"
        "</div>"
    )

    def delete(self, request, *args, **kwargs):
        """Override delete and display success message
        :param request: request
            Django uses request and response objects to pass state through the system
        :return:
            himself
        :rtype: form_valid
        """
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)
