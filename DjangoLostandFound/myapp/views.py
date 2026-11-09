from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.shortcuts import redirect

from .forms import SignUpForm
from .pages import home_page, login_page, signup_page


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