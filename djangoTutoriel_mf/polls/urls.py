from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

from . import views

app_name = "polls"

"""
Configuration des URL de l'application Polls.

Ce module définit les routes accessibles dans l'application
et associe chaque URL à une vue Django correspondante.
"""

urlpatterns = [
    path("", views.index, name="index"),
    path("all/", views.all_questions, name="all"),
    path(
        "<int:question_id>/frequency/",
        views.frequency,
        name="frequency",
    ),
    path("statistics/", views.statistics, name="statistics"),
    path("add/", views.add_question, name="add"),
    path("<int:question_id>/vote/", views.vote, name="vote"),
    path(
        "login/",
        LoginView.as_view(template_name="polls/login.html"),
        name="login",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
]