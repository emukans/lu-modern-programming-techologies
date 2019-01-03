from django.urls import path

from . import views

urlpatterns = [
    path('tournament/', views.tournament_statistics, name='tournament-statistics'),
    path('tournament/team/<int:team_id>', views.team_statistics, name='team-statistics'),
]
