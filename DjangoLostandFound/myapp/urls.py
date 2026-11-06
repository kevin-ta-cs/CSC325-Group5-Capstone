from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', LoginView.as_view(next_page='/'), name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
]