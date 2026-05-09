from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('admin/users/', views.user_list, name='user_list'),
    path('admin/organizers/', views.organizer_list, name='organizer_list'),
    path('admin/users/<int:user_id>/', views.user_detail, name='user_detail'),
]

