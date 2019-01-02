from django.urls import path

from . import views

urlpatterns = [
    path('tournament/', views.tournament_statistics),
]
