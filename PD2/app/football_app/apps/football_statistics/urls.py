from django.urls import path

from . import views

urlpatterns = [
    path('tournament/tables/', views.tournament_table),
]
