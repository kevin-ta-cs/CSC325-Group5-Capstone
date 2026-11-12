from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('items/', views.browse_items, name='browse_items'),
    path('login/', views.PythonLoginView.as_view(next_page='/'), name='login'),
    path('signup/', views.signup, name='signup'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('report/found/', views.report_found_item, name='found_report'),
    path(
        'report/found/<str:item_id>/image/',
        views.found_item_image,
        name='found_item_image',
    ),
    path(
        'report/found/<str:item_id>/approve-image/',
        views.approve_found_item_image,
        name='approve_found_item_image',
    ),
    path('items/<str:item_id>/', views.found_item_detail, name='found_item_detail'),
    path(
        'report/found/<str:item_id>/request/',
        views.request_found_item_information,
        name='request_found_item_information',
    ),
    path(
        'report/found/<str:item_id>/',
        views.found_item_detail,
        name='found_item_detail_legacy',
    ),
    path('report/found/<str:item_id>/edit/', views.edit_found_item, name='edit_found_item'),
    path('report/found/<str:item_id>/delete/', views.delete_found_item, name='delete_found_item'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
]