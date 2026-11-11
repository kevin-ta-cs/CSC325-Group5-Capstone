from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect

from .forms import DashboardUsernameForm, FoundItemForm, SignUpForm
from .pages import (
    found_item_page,
    home_page,
    login_page,
    signup_page,
    user_dashboard_page,
)


def home(request):
    return HttpResponse(home_page(request))


class PythonLoginView(LoginView):
    def render_to_response(self, context, **response_kwargs):
        return HttpResponse(
            login_page(self.request, context["form"], context.get("next", ""))
        )


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = False
            user.is_superuser = False
            user.save()
            form.save_m2m()
            return redirect('login')
    else:
        form = SignUpForm()

    return HttpResponse(signup_page(request, form))


@login_required(login_url='login')
def user_dashboard(request):
    form = DashboardUsernameForm(
        request.POST if request.method == 'POST' else None,
        instance=request.user,
    )
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Your username was updated.')
            return redirect('user_dashboard')

    return HttpResponse(user_dashboard_page(request, form))


@login_required(login_url='login')
def report_found_item(request):
    form = FoundItemForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        found_item = form.save(commit=False)
        found_item.reporter = request.user
        found_item.save()
        messages.success(request, 'Your found item was reported.')
        return redirect('found_report')

    return HttpResponse(found_item_page(request, form))