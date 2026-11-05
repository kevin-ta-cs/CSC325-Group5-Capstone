from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import redirect, render


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