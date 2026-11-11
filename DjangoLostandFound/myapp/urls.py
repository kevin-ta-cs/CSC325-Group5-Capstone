from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.PythonLoginView.as_view(next_page='/'), name='login'),
    path('signup/', views.signup, name='signup'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('report/found/', views.report_found_item, name='found_report'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
]