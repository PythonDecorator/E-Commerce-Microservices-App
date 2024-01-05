"""
Users urls
"""

from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [
    path('register/', views.CreateUserView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name="login"),
    path('logout/', views.LogoutAPIView.as_view(), name="logout"),
    path('profile/me/', views.ManageUserView.as_view(), name="me"),
    path('users/all/', views.UsersAPIView.as_view(), name="users"),
]
