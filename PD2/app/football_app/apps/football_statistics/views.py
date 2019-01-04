from django.http import HttpRequest
from django.shortcuts import render

from .utils import statistics


def tournament_statistics(request: HttpRequest):
    return render(request, 'football_statistics/tournament_statistics.html', dict(
        team_list=statistics.build_team_list(),
        best_player_list=statistics.build_best_player_list(),
        best_goalkeeper_list=statistics.build_best_goalkeeper_list(),
        aggressive_player_list=statistics.build_most_aggressive_player_list(),
        tight_referee_list=statistics.build_most_tight_referee_list(),
        effective_player_list=statistics.build_most_effective_player(),
        effective_goalkeeper_list=statistics.build_most_effective_goalkeeper()
    ))


def team_statistics(request: HttpRequest, team_id):
    return render(request, 'football_statistics/team_statistics.html', dict(
        player_list=statistics.build_player_list(team_id),
        goalkeeper_list=statistics.build_goalkeeper_list(team_id),
    ))
