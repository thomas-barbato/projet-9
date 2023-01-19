from django.views.generic import View
from django.http import HttpResponse
from django.views import View
from urllib import response
from django.apps import apps
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, HttpResponseRedirect


class LoginView(View):
    template_name = 'login.html'
