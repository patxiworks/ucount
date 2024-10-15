# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# Create your views here.
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import LoginForm, SignUpForm
from backend.models import E5Centres
from backend.context import check_valid_user


def login_view(request):
    form = LoginForm(request.POST or None)
    msg = None
    usercheck = None

    if request.method == "POST":

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                msg = 'Invalid credentials'
        else:
            msg = 'Error validating the form'
    else:
        if not request.user.is_anonymous:
            return redirect("/")

    return render(request, "backend/accounts/login.html", {"form": form, "msg": msg})


def logout_view(request):
    form = LoginForm(request.POST or None)
    msg = "You were successfully logged out"
    logout(request)
    return render(request, "backend/accounts/login.html", {"form": form, "msg": msg})


@require_http_methods(["POST"])
def switch_session(request, ctr_id, user_id):
    valid = check_valid_user(request)
    if 'validuser' in valid and valid['validuser']:
        user = request.user.userstatus
        if ctr_id:
            user.centre = E5Centres.objects.get(pk=ctr_id)
        else:
            user.centre = None
        user.save()
    return redirect("/")


def register_user(request):
    msg = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)

            msg = 'User created - please <a href="/login">login</a>.'
            success = True

            # return redirect("/login/")

        else:
            msg = 'Form is not valid'
    else:
        form = SignUpForm()

    return render(request, "backend/accounts/register.html", {"form": form, "msg": msg, "success": success})
