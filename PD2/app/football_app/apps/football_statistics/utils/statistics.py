from functools import reduce
from collections import Counter
from django.db.models import Count

from football_app.apps.football.models import Team, Player, Goal, Match, Foul, BaseTeamOnMatch

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
    if len(data_list) == 0:
        return {}

    return reduce(lambda x, y: dict(Counter(x) + Counter(y)), data_list)


def process_team_data(team: Team) -> dict:
    games_played = Match.objects.filter(home_team=team).count() + Match.objects.filter(guest_team=team).count()
    team_match_list = Match.objects.filter(home_team=team) | Match.objects.filter(guest_team=team)
    match_data_list = [process_team_match(match, team) for match in team_match_list]
    match_data = reduce_list_of_dicts(match_data_list)

    team_data = dict(id=team.id,
                     games_played=games_played,
                     name=team.name,
                     goals_scored=match_data.get('goals_scored', 0),
                     goals_conceded=match_data.get('goal_conceded', 0),
                     won_count=match_data.get('won_count', 0),
                     lost_count=(games_played - match_data.get('won_count', 0)),
                     won_in_primary_time=match_data.get('won_in_primary_time', 0),
                     won_in_extra_time=match_data.get('won_count', 0) - match_data.get('won_in_primary_time', 0),
                     lost_in_primary_time=match_data.get('lost_in_primary_time', 0),
                     lost_in_extra_time=(games_played - match_data.get('won_count', 0)) - match_data.get('lost_in_primary_time', 0))

    team_data.update({
        'points': team_data.get('won_in_primary_time', 0) * 5 + team_data.get('won_in_extra_time', 0) * 3
                  + team_data.get('lost_in_extra_time', 0) * 2 + team_data.get('lost_in_primary_time', 0)
    })
    return team_data


def process_player_data(player: Player) -> dict:
    return dict(
        first_name=player.first_name,
        last_name=player.last_name,
        team_name=player.team.name,
        number=player.number,
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


def get_played_time_in_match(match: Match, player: Player) -> tuple:
    played_from = 0
    played_till = PRIMARY_TIME_LIMIT

    if Goal.objects.filter(match=match, minute__gt=PRIMARY_TIME_LIMIT).exists():
        last_goal = Goal.objects.filter(match=match, minute__gt=PRIMARY_TIME_LIMIT).order_by('minute').last()
        played_till = get_extra_time_period_end(last_goal.minute, PRIMARY_TIME_LIMIT)

    if match.change_set.filter(replaced_from=player).exists():
        played_till = match.change_set.filter(replaced_from=player).first().minute

    if match.change_set.filter(replaced_to=player).exists():
        played_from = match.change_set.filter(replaced_to=player).first().minute

    return played_from, played_till


def count_goalkeeper_conceded_goals_on_match(match: Match, player: Player) -> dict:
    count_goals_from_time, count_goals_till_time = get_played_time_in_match(match, player)
    goalkeeper_data = dict(
        conceded_goal_count=0
    )

    conceded_goal_list = Goal.objects.filter(match=match, minute__gte=count_goals_from_time, minute__lte=count_goals_till_time).exclude(player__team=player.team)
    if not conceded_goal_list.count():
        return goalkeeper_data

    goalkeeper_data.update(dict(conceded_goal_count=conceded_goal_list.count()))

    return goalkeeper_data


def process_goalkeeper_data(player: Player) -> dict:
    participated_match_list = get_player_match_list(player)
    player_data = dict(
        first_name=player.first_name,
        last_name=player.last_name,
        team_name=player.team.name,
        number=player.number,
        conceded_goal_count=0,
        participated_match_count=0,
        average_conceded_goal_count=0
    )
    if not participated_match_list.count():
        return player_data

    goalkeeper_data = reduce_list_of_dicts([count_goalkeeper_conceded_goals_on_match(match, player) for match in participated_match_list])

    return dict(
        first_name=player.first_name,
        last_name=player.last_name,
        team_name=player.team.name,
        number=player.number,
        conceded_goal_count=goalkeeper_data.get('conceded_goal_count', 0),
        participated_match_count=participated_match_list.count(),
        average_conceded_goal_count=round(goalkeeper_data.get('conceded_goal_count', 0) / participated_match_list.count(), 1)
    )


def get_player_match_list(player: Player):
    participated_match_list = Match.objects.filter(baseteamonmatch__base_players=player, baseteamonmatch__team=player.team).distinct() | Match.objects.filter(
        change__replaced_to=player).distinct()
    return participated_match_list


def build_best_goalkeeper_list() -> list:
    goalkeeper_list = Player.objects.filter(role=Player.GOALKEEPER)
    goalkeeper_data = list(map(process_goalkeeper_data, goalkeeper_list))

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


def build_most_tight_referee_list() -> list:
    referee_foul_count = Match.objects.values('main_referee__id', 'main_referee__first_name', 'main_referee__last_name').annotate(foul_count=Count('foul')) \
        .order_by('main_referee__first_name', 'main_referee__last_name')

    referee_data = list(map(lambda match: dict(first_name=match['main_referee__first_name'],
                                               last_name=match['main_referee__last_name'],
                                               average_foul_count=match['foul_count'] / Match.objects.filter(main_referee_id=match['main_referee__id']).count()),
                            referee_foul_count))

    return sorted(referee_data, key=lambda k: (k['average_foul_count']), reverse=True)


def build_most_effective_goalkeeper() -> list:
    player_list = Player.objects.filter(role=Player.GOALKEEPER)
    player_data = map(lambda player: {**process_goalkeeper_data(player), **process_player_additional_data(player)}, player_list)
    player_data = map(lambda player: {**player, **{'player_score': calculate_goalkeeper_score(player)}}, player_data)
    player_data = sorted(player_data, key=lambda k: k['player_score'], reverse=True)

    return list(player_data)[:5]


def calculate_goalkeeper_score(player):
    drawbacks = (player.get('conceded_goal_count', 0) + player.get('yellow_card_count', 0) + player.get('red_card_count', 0)) + 1

    return round(player.get('played_length', 0) / drawbacks, 2)


def build_most_effective_player() -> list:
    player_list = Player.objects.exclude(role=Player.GOALKEEPER)
    player_data = map(lambda player: {**process_player_data(player), **process_player_additional_data(player)}, player_list)
    player_data = map(lambda player: {**player, **{'player_score': calculate_player_score(player)}}, player_data)
    player_data = sorted(player_data, key=lambda k: k['player_score'], reverse=True)

    return list(player_data)[:10]


def calculate_player_score(player):
    score = (player.get('goals_scored', 0) + player.get('goals_assisted', 0) - player.get('yellow_card_count', 0) - player.get('red_card_count', 0)) * 1000 / player.get(
        'played_length', 1)
    return round(score, 2)


def build_team_list():
    team_list = map(process_team_data, Team.objects.all())
    sorted_team_list = sorted(team_list, key=lambda k: k['points'], reverse=True)

    return sorted_team_list


def process_player_match_data(match: Match, player: Player) -> dict:
    played_from, played_till = get_played_time_in_match(match, player)
    foul_count = Foul.objects.filter(player=player, match=match).count()

    return dict(
        played_length=(played_till - played_from),
        yellow_card_count=1 if foul_count else 0,
        red_card_count=1 if foul_count > 1 else 0,
        match_count=1,
        match_count_in_base_team=1 if BaseTeamOnMatch.objects.filter(base_players=player, match=match).distinct().count() else 0
    )


def process_player_additional_data(player: Player):
    participated_match_list = get_player_match_list(player)

    return reduce_list_of_dicts([process_player_match_data(match, player) for match in participated_match_list])


def build_player_list(team_id: int) -> list:
    player_list = Player.objects.filter(team_id=team_id).exclude(role=Player.GOALKEEPER).order_by('number')
    player_data = map(lambda player: {**process_player_data(player), **process_player_additional_data(player)}, player_list)

    return list(player_data)


def build_goalkeeper_list(team_id: int) -> list:
    player_list = Player.objects.filter(team_id=team_id, role=Player.GOALKEEPER).order_by('number')
    player_data = map(lambda player: {**process_goalkeeper_data(player), **process_player_additional_data(player)}, player_list)

    return list(player_data)
