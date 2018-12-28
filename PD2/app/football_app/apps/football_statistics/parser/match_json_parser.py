from django.db import IntegrityError, transaction

from football_app.apps.football.models import Stadium, Team, Player, Referee
from football_app.apps.football_statistics.models import Match, BaseTeamOnMatch
import datetime


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
                date=datetime.datetime.strptime(match_data['Laiks'], '%Y/%m/%d'),
                viewers=int(match_data['Skatitaji']),
                stadium=stadium,
                home_team=home_team,
                guest_team=guest_team,
                main_referee=parse_referee_json(match_data['VT'])
            )

            if is_match_created:
                parse_base_team_on_match_json(match, home_team, match_data['Komanda'][0]['Pamatsastavs']['Speletajs'])
                parse_base_team_on_match_json(match, guest_team, match_data['Komanda'][1]['Pamatsastavs']['Speletajs'])

                match.line_referee.set([parse_referee_json(referee) for referee in match_data['T']])
                match.save()

    except IntegrityError as e:
        print(e)

    except Exception as e:
        print(e)
