from django.http import HttpRequest
from django.shortcuts import render
from functools import reduce
from collections import Counter

from football_app.apps.football.models import Team
from football_app.apps.football_statistics.models import Goal, Match


def process_team_match(match: Match, team: Team) -> dict:
    goal_list = Goal.objects.filter(match=match, player__team=team).order_by('minute')
    goal_conceded_list = Goal.objects.exclude(player__team=team).filter(match=match).order_by('minute')
    goals_scored = goal_list.count()
    goal_conceded = goal_conceded_list.count()
    is_won = goals_scored > goal_conceded
    last_goal = goal_list.last() if is_won else goal_conceded_list.last()
    is_won_in_primary_time = is_won and last_goal.minute < 60
    is_lost_in_primary_time = not is_won and last_goal.minute < 60

    return dict(
        goals_scored=goals_scored,
        goal_conceded=goal_conceded,
        won_count=int(is_won),
        won_in_primary_time=int(is_won_in_primary_time),
        lost_in_primary_time=int(is_lost_in_primary_time),
    )


def process_team_data(team: Team) -> dict:
    games_played = Match.objects.filter(home_team=team).count() + Match.objects.filter(guest_team=team).count()
    team_match_list = Match.objects.filter(home_team=team) | Match.objects.filter(guest_team=team)
    match_data_list = [process_team_match(match, team) for match in team_match_list]
    match_data = reduce(lambda x, y: dict(Counter(x) + Counter(y)), match_data_list)

    team_data = dict(games_played=games_played,
                     name=team.name,
                     goals_scored=match_data.get('goals_scored'),
                     goals_conceded=match_data.get('goal_conceded'),
                     won_count=match_data.get('won_count'),
                     lost_count=(games_played - match_data.get('won_count')),
                     won_in_primary_time=match_data.get('won_in_primary_time'),
                     won_in_extra_time=match_data.get('won_count') - match_data.get('won_in_primary_time'),
                     lost_in_primary_time=match_data.get('lost_in_primary_time'),
                     lost_in_extra_time=(games_played - match_data.get('won_count')) - match_data.get('lost_in_primary_time'))

    team_data.update({
        'points': team_data.get('won_in_primary_time') * 5 + team_data.get('won_in_extra_time') * 3
        + team_data.get('lost_in_extra_time') * 2 + team_data.get('lost_in_primary_time')
    })
    return team_data


def tournament_table(request: HttpRequest):
    team_list = map(process_team_data, Team.objects.all())
    sorted_team_list = sorted(team_list, key=lambda k: k['points'], reverse=True)

    return render(request, 'football_statistics/table/tournament.html', dict(
        team_list=sorted_team_list
    ))
