""" imports """
import datetime
from itertools import chain

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


class CreateUserView(FormView, JsonableResponseMixin, SuccessMessageMixin):
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

    def get_success_message(self, cleaned_data=""):
        return self.success_message

    def form_valid(self, form):
        """Override form_valid to create user and add 'is_active', 'date_joined', 'is_staff', and custom success msg
        :param form: SignupForm, used to create user.
        :type form: form
        :return: JsonResponse with response message and status 200 if request is ajax type
         else return JsonableResponseMixin form_valid
        :rtype: Ajax
        """

        # TODO: You can use a form here to validate the data
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
                messages.success(self.request, self.get_success_message())
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


class LoginAjaxView(LoginView, SuccessMessageMixin):
    """Check user, login and redirect to flux_view
    :Ancestor: LoginView
        Display login form and handle login action
    :return: "authentication/login.html"
    :rtype: Template
    """

    form_class = SigninForm
    redirect_authenticated_user = True
    success_url = "dashboard/flux"
    success_message = (
        '<div class="alert alert-success text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
        "<p>Vous êtes maintenant connecté.</p>"
        "</div>"
    )

    def get_success_message(self, cleaned_data=""):
        return self.success_message

    def get_success_url(self):
        """success url set to redirect after login in
        :Argument: self
        :type self : /
        :return: redirection to flux_view
        :rtype: str
        """
        return reverse_lazy("flux_view")

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
        response = ""
        if user is not None:
            login(self.request, user)
            response = {"status": 1}
            messages.success(self.request, self.get_success_message())
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
        reviews = Review.objects.annotate(post_type=Value("Review"))
        ticket = Ticket.objects.annotate(post_type=Value("Ticket"))

        result = sorted(
            list(chain(reviews, ticket)), key=lambda d: d.time_created, reverse=True
        )

        context["posts"] = result
        context["rating_range"] = range(5)
        return context


class CreateTicketView(FormView, LoginRequiredMixin, SuccessMessageMixin):
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

    def get_success_message(self, cleaned_data=""):
        return self.success_message

    def form_valid(self, form):
        """Override form_valid, save ticket and return himself
        :param form: form
            return validation error and redirect to success url
        :return:
            himself
        :rtype: form_valid
        """
        form.save(user=self.request.user, file=self.request.FILES["image"])
        messages.success(self.request, self.get_success_message())
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        """Override form_invalid, add error message
        :param form: form
            return validation error and redirect to success url
        :return:
            himself
        :rtype: form_invalid
        """
        messages.error(self.request, self.error_message)
        return super().form_invalid(form)


class CreateFullReviewView(CreateView, LoginRequiredMixin, SuccessMessageMixin):
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

    def get_success_message(self, cleaned_data=""):
        return self.success_message

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
            messages.success(self.request, self.success_message)
        return HttpResponseRedirect(reverse("flux_view"))

    def form_invalid(self, form):
        """Override form_invalid, display error message
        :param form: form
            return validation
        :return:
            himself
        :rtype: form_invalid
        """
        messages.error(self.request, self.error_message)
        return HttpResponseRedirect(reverse("create_review_view"))


class CreateReviewView(CreateView, LoginRequiredMixin, SuccessMessageMixin):
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

    def get_success_message(self, cleaned_data=""):
        return self.success_message

    def get_context_data(self, **kwargs):
        """Override get_context_data to return form
        :param kwargs: kwargs.
        :return: context
        :rtype: list
        """
        context = super().get_context_data(**kwargs)
        ticket_id = self.kwargs["id"]
        # TODO: Remove ticket = list(
        #     Ticket.objects.select_related(
        #         "user",
        #         "ticket",
        #         "ticket__user_id__username",
        #         "user__username",
        #         "user_id__username",
        #     )
        #     .filter(id=ticket_id)
        #     .values(
        #         "id",
        #         "title",
        #         "description",
        #         "image",
        #         "time_created",
        #         "user_id",
        #         "user_id__username",
        #     )
        # )
        ticket = Ticket.objects.get(id=ticket_id)
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
            messages.success(self.request, self.get_success_message())
        else:
            messages.error(self.request, self.error_message2)
        return HttpResponseRedirect(reverse("flux_view"))

    def form_invalid(self, form):
        """Override form_invalid, display error message
        :param form: form
            return validation
        :return:
            himself
        :rtype: form_invalid
        """
        messages.error(self.request, self.error_message)
        return HttpResponseRedirect(reverse("create_review_view"))


class DisplayPostsView(TemplateView, LoginRequiredMixin):
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

        # TODO: Please change what I changed in fluxview
        query_review = (
            Review.objects.select_related("user", "ticket")
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
            )
            .filter(user_id=self.request.user.id)
            .annotate(post_type=Value("Review"))
        )

        query_ticket = (
            Ticket.objects.all()
            .filter(user_id=self.request.user.id)
            .select_related("user")
            .annotate(post_type=Value("Ticket"))
        )
        queries = sorted(
            list(chain(query_ticket.values(), query_review)),
            key=lambda d: d["time_created"],
            reverse=True,
        )

        if len(queries) == 0:
            messages.warning(self.request, self.empty_content_message)
        else:
            context["posts"] = queries
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

        # TODO: Use Review.objects.get and get_queryset for this
        context["body_content"] = Review.objects.filter(
            id=self.kwargs["pk"], user_id=self.request.user.id
        ).values()[0]["body"]
        return context


class UpdateTicket(UpdateView, LoginRequiredMixin, SuccessMessageMixin):
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

    def get_success_message(self, cleaned_data=""):
        return self.success_message

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
            # TODO: This should be in a form like what did last time
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
            messages.success(self.request, self.get_success_message())
        return HttpResponseRedirect(reverse("posts_view"))


class DeletePost(DeleteView, LoginRequiredMixin, SuccessMessageMixin):
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

    def get_success_message(self, cleaned_data=""):
        return self.success_message

    def delete(self, request, *args, **kwargs):
        """Override delete and display success message
        :param request: request
            Django uses request and response objects to pass state through the system
        :return:
            himself
        :rtype: form_valid
        """

        # TODO: No need for select related here
        #   No need for values here
        ticket_image = (
            Review.objects.select_related("ticket")
            .filter(user_id=self.request.user.id)
            .values("ticket__image")[0]["ticket__image"]
        )
        HandleUploadedFile.delete_standalone_img(filename=ticket_image)
        messages.success(self.request, self.get_success_message())
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


class DisplaySuscribeView(ListView, LoginRequiredMixin, SuccessMessageMixin):
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
    error_message = (
        '<div class="alert alert-info text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
        "<p>l'utilisateur que vous recherchez n'existe pas.</p>"
        "</div>"
    )
    warning_message = (
        '<div class="alert alert-info text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
        "<p>Vous suivez déjà cet utilisateur.</p>"
        "</div>"
    )

    def get_success_message(self, cleaned_data):
        return (
            '<div class="alert alert-success text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
            f"<p>Vous suivez maintenant <b>{cleaned_data}</b>.</p>"
            "</div>"
        )

    # TODO: If no specific mixin for it no worries
    #   No need for an extra method for a simple string
    def get_warning_message(self):
        """Display warning message.
        :Ancestors: None
        :return:
            warning msg
        :rtype: Template
            str
        """
        return self.warning_message

    # TODO: If no specific mixin for it no worries
    #   No need for an extra method for a simple string
    def get_error_message(self):
        """Display error message.
        :Ancestors: None
        :return:
            error msg
        :rtype: Template
            str
        """
        return self.error_message

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

        # TODO: Use CreateBaseView here, you have it at the same time thant ListView
        #   Please use a form for this
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
                messages.success(self.request, self.get_success_message(username))
            else:
                messages.warning(self.request, self.get_warning_message())
        else:
            messages.error(self.request, self.get_error_message())

        return HttpResponseRedirect(reverse("suscribe_view"))


class UnfollowUser(SuccessMessageMixin, DeleteView, LoginRequiredMixin):
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

    def get_success_message(self, cleaned_data=""):
        return self.success_message

    def delete(self, request, *args, **kwargs):
        """Override delete and display success message
        :param request: request
            Django uses request and response objects to pass state through the system
        :return:
            himself
        :rtype: form_valid
        """
        messages.success(self.request, self.get_success_message())
        return super().delete(request, *args, **kwargs)
