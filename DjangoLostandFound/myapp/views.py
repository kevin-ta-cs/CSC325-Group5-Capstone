from django.shortcuts import redirect, render
from .forms import SignUpForm

# Create your views here.
from django.http import HttpResponse

def home(request):
    return render(request, 'index.html')


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

    return render(request, 'registration/signup.html', {'form': form})