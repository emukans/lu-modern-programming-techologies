from django.db import IntegrityError, transaction
from datetime import datetime
from football_app.apps.football.models import Stadium, Team, Player, Referee
from football_app.apps.football_statistics.models import Match, BaseTeamOnMatch, Foul, Goal, GoalCombination, Change


def parse_time(time: str) -> tuple:
    parsed_time = time.split(':')

    return int(parsed_time[0]), int(parsed_time[1])


def parse_change_json(match: Match, team: Team, data):
    if type(data) is str:
        return None

    data_to_parse = []
    if type(data['Maina']) is dict:
        data_to_parse.append(data['Maina'])

    if type(data['Maina']) is list:
        data_to_parse = data['Maina']

    change_list = map(lambda change: Change(
        match=match,
        replaced_from=Player.objects.get(number=change['Nr1'], team=team),
        replaced_to=Player.objects.get(number=change['Nr2'], team=team),
        minute=parse_time(change['Laiks'])[0],
        second=parse_time(change['Laiks'])[1]
    ), data_to_parse)
    Change.objects.bulk_create(change_list)


def parse_foul_json(match: Match, team: Team, data):
    if type(data) is str:
        return None

    data_to_parse = []
    if type(data['Sods']) is dict:
        data_to_parse.append(data['Sods'])

    if type(data['Sods']) is list:
        data_to_parse = data['Sods']

    foul_list = map(lambda foul: Foul(
        match=match,
        player=Player.objects.get(number=foul['Nr'], team=team),
        minute=parse_time(foul['Laiks'])[0],
        second=parse_time(foul['Laiks'])[1]
    ), data_to_parse)
    Foul.objects.bulk_create(foul_list)


def parse_goal(match: Match, team: Team, goal_data):
    goal = Goal(
        match=match,
        player=Player.objects.get(number=goal_data['Nr'], team=team),
        minute=parse_time(goal_data['Laiks'])[0],
        second=parse_time(goal_data['Laiks'])[1],
        goal_type=goal_data['Sitiens']
    )
    goal.save()

    if goal_data.get('P'):
        goal_combination = GoalCombination(goal=goal)
        goal_combination.save()
        combination_player_list = []

        if type(goal_data['P']) is list:
            combination_player_list = map(lambda player: Player.objects.get(number=player['Nr'], team=team), goal_data['P'])
        else:
            combination_player_list.append(Player.objects.get(number=goal_data['Nr'], team=team))

        goal_combination.participated_players.set(combination_player_list)
        goal_combination.save()


def parse_goal_json(match: Match, team: Team, data):
    if type(data) is str:
        return None

    data_to_parse = []
    if type(data['VG']) is dict:
        data_to_parse.append(data['VG'])

    if type(data['VG']) is list:
        data_to_parse = data['VG']

    for goal in data_to_parse:
        parse_goal(match, team, goal)


def parse_base_team_on_match_json(match: Match, team: Team, data: list):
    base_team, is_created = BaseTeamOnMatch.objects.get_or_create(match=match, team=team)

    if not is_created:
        return

    number_of_players_on_match = map(lambda player: int(player['Nr']), data)
    players_on_match = Player.objects.filter(number__in=number_of_players_on_match)
    base_team.base_players.set(players_on_match)
    base_team.save()


def parse_referee_json(data: dict) -> Referee:
    referee, _ = Referee.objects.get_or_create(
        first_name=data['Vards'],
        last_name=data['Uzvards']
    )

    return referee


def parse_team_json(data: dict) -> Team:
    team, is_team_created = Team.objects.get_or_create(
        name=data['Nosaukums']
    )

    if is_team_created:
        player_list = map(lambda player: Player(
            first_name=player['Vards'],
            last_name=player['Uzvards'],
            number=player['Nr'],
            role=player['Loma'],
            team=team
        ), data['Speletaji']['Speletajs'])

        Player.objects.bulk_create(player_list)

    return team


def match_json_parser(data: dict):
    try:
        with transaction.atomic():
            match_data = data['Spele']
            stadium, _ = Stadium.objects.get_or_create(name=match_data['Vieta'])

            home_team = parse_team_json(match_data['Komanda'][0])
            guest_team = parse_team_json(match_data['Komanda'][1])
            match, is_match_created = Match.objects.get_or_create(
                date=datetime.strptime(match_data['Laiks'], '%Y/%m/%d'),
                viewers=int(match_data['Skatitaji']),
                stadium=stadium,
                home_team=home_team,
                guest_team=guest_team,
                main_referee=parse_referee_json(match_data['VT'])
            )

            if is_match_created:
                parse_base_team_on_match_json(match, home_team, match_data['Komanda'][0]['Pamatsastavs']['Speletajs'])
                parse_base_team_on_match_json(match, guest_team, match_data['Komanda'][1]['Pamatsastavs']['Speletajs'])

                parse_foul_json(match, home_team, match_data['Komanda'][0]['Sodi'])
                parse_foul_json(match, guest_team, match_data['Komanda'][1]['Sodi'])

                parse_goal_json(match, home_team, match_data['Komanda'][0]['Varti'])
                parse_goal_json(match, guest_team, match_data['Komanda'][1]['Varti'])

                parse_change_json(match, home_team, match_data['Komanda'][0]['Mainas'])
                parse_change_json(match, guest_team, match_data['Komanda'][1]['Mainas'])

                match.line_referee.set([parse_referee_json(referee) for referee in match_data['T']])
                match.save()

    except IntegrityError as e:
        print(e)

    except Exception as e:
        import sys
        import os
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
