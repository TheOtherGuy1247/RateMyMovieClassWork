from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("signup/", views.signup, name="signup"),
    path("usersignup/", views.UsersingupView.as_view(), name="usersignup"),
]