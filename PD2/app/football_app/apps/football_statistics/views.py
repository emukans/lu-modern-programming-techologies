from typing import Optional
from django.http import HttpRequest
from django.shortcuts import render
from functools import reduce
from collections import Counter
from django.db.models import Count

from football_app.apps.football.models import Team, Player
from football_app.apps.football_statistics.models import Goal, Match

PRIMARY_TIME_LIMIT = 60
EXTRA_PERIOD_TIME_LENGTH = 15


def process_team_match(match: Match, team: Team) -> dict:
    goal_list = Goal.objects.filter(match=match, player__team=team).order_by('minute')
    goal_conceded_list = Goal.objects.exclude(player__team=team).filter(match=match).order_by('minute')
    goals_scored = goal_list.count()
    goal_conceded = goal_conceded_list.count()
    is_won = goals_scored > goal_conceded
    last_goal = goal_list.last() if is_won else goal_conceded_list.last()
    is_won_in_primary_time = is_won and last_goal.minute < PRIMARY_TIME_LIMIT
    is_lost_in_primary_time = not is_won and last_goal.minute < PRIMARY_TIME_LIMIT

    return dict(
        goals_scored=goals_scored,
        goal_conceded=goal_conceded,
        won_count=int(is_won),
        won_in_primary_time=int(is_won_in_primary_time),
        lost_in_primary_time=int(is_lost_in_primary_time),
    )


def reduce_list_of_dicts(data_list: list) -> dict:
    return reduce(lambda x, y: dict(Counter(x) + Counter(y)), data_list)


def process_team_data(team: Team) -> dict:
    games_played = Match.objects.filter(home_team=team).count() + Match.objects.filter(guest_team=team).count()
    team_match_list = Match.objects.filter(home_team=team) | Match.objects.filter(guest_team=team)
    match_data_list = [process_team_match(match, team) for match in team_match_list]
    match_data = reduce_list_of_dicts(match_data_list)

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


def process_player_data(player: Player) -> dict:
    return dict(
        first_name=player.first_name,
        last_name=player.last_name,
        team_name=player.team.name,
        goals_scored=player.goal_set.count(),
        goals_assisted=player.goalcombination_set.count()
    )


def build_best_player_list() -> list:
    best_player_list = Player.objects.annotate(goal_count=Count('goal'), combination_count=Count('goalcombination')) \
        .order_by('-goal_count', '-combination_count', 'first_name', 'last_name')[:10]

    player_list = map(process_player_data, best_player_list)
    return list(player_list)


def get_extra_time_period_end(last_goal_time: int, accumulator: int) -> int:
    if last_goal_time > accumulator:
        return get_extra_time_period_end(last_goal_time, accumulator + EXTRA_PERIOD_TIME_LENGTH)

    return accumulator


def count_goalkeeper_conceded_goals_on_match(match: Match, player: Player) -> dict:
    count_goals_from_time = 0
    count_goals_till_time = PRIMARY_TIME_LIMIT
    goalkeeper_data = dict(
        conceded_goal_count=0
    )

    if Goal.objects.filter(match=match, minute__gt=PRIMARY_TIME_LIMIT).exists():
        last_goal = Goal.objects.filter(match=match, minute__gt=PRIMARY_TIME_LIMIT).order_by('minute').last()
        count_goals_till_time = get_extra_time_period_end(last_goal.minute, PRIMARY_TIME_LIMIT)

    if match.change_set.filter(replaced_from=player).exists():
        count_goals_till_time = match.change_set.filter(replaced_from=player).first().minute

    if match.change_set.filter(replaced_to=player).exists():
        count_goals_from_time = match.change_set.filter(replaced_to=player).first().minute

    conceded_goal_list = Goal.objects.filter(match=match, minute__gte=count_goals_from_time, minute__lte=count_goals_till_time).exclude(player__team=player.team)
    if not conceded_goal_list.count():
        return goalkeeper_data

    goalkeeper_data.update(dict(conceded_goal_count=conceded_goal_list.count()))

    return goalkeeper_data


def process_goalkeeper_data(player: Player) -> Optional[dict]:
    participated_match_list = Match.objects.filter(baseteamonmatch__base_players=player, baseteamonmatch__team=player.team).distinct() | Match.objects.filter(change__replaced_to=player).distinct()

    if not participated_match_list.count():
        return None

    goalkeeper_data = reduce_list_of_dicts([count_goalkeeper_conceded_goals_on_match(match, player) for match in participated_match_list])

    return dict(
        first_name=player.first_name,
        last_name=player.last_name,
        team_name=player.team.name,
        conceded_goal_count=goalkeeper_data.get('conceded_goal_count'),
        participated_match_count=participated_match_list.count(),
        average_conceded_goal_count=round(participated_match_list.count() / goalkeeper_data.get('conceded_goal_count'), 1)
    )


def build_best_goalkeeper_list() -> list:
    goalkeeper_list = Player.objects.filter(role=Player.GOALKEEPER)
    goalkeeper_data = list(filter(lambda x: x is not None, map(process_goalkeeper_data, goalkeeper_list)))

    return sorted(goalkeeper_data, key=lambda k: k['average_conceded_goal_count'])[:5]


def process_aggressive_player(player: Player) -> dict:
    return dict(
        first_name=player.first_name,
        last_name=player.last_name,
        team_name=player.team.name,
        foul_count=player.foul_set.count()
    )


def build_most_aggressive_player_list() -> list:
    aggressive_player_list = Player.objects.annotate(foul_count=Count('foul')).exclude(foul_count=0).order_by('-foul_count', 'first_name', 'last_name')[:10]

    player_list = map(process_aggressive_player, aggressive_player_list)
    return list(player_list)


def tournament_statistics(request: HttpRequest):
    team_list = map(process_team_data, Team.objects.all())
    sorted_team_list = sorted(team_list, key=lambda k: k['points'], reverse=True)

    return render(request, 'football_statistics/statistics.html', dict(
        team_list=sorted_team_list,
        best_player_list=build_best_player_list(),
        best_goalkeeper_list=build_best_goalkeeper_list(),
        aggressive_player_list=build_most_aggressive_player_list()
    ))
