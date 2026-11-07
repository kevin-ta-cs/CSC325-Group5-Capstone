from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import LostItemForm


def home(request):
    return render(request, 'index.html')


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect("home")
    else:
        form = UserCreationForm()

    return render(request, "register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect("home")
    else:
        form = AuthenticationForm(request)

    return render(request, "login.html", {"form": form})


def logout_view(request):
    if request.method != "POST":
        return redirect("home")

    auth_logout(request)
    return redirect("home")


@login_required(login_url="login")
def report_lost_item(request):
    if request.method == "POST":
        form = LostItemForm(request.POST)
        if form.is_valid():
            lost_item = form.save(commit=False)
            lost_item.submitted_by = request.user
            lost_item.save()
            messages.success(request, "Your lost-item report was submitted.")
            return redirect("report_lost_item")
    else:
        form = LostItemForm()

    return render(request, "report_lost_item.html", {"form": form})