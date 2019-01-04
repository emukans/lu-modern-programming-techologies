from datetime import datetime

from django.core.exceptions import ValidationError

from football_app.apps.football.models import Match


def match_json_validator(json_data: dict):
    guest_team_name = json_data['Spele']['Komanda'][0]['Nosaukums']
    home_team_name = json_data['Spele']['Komanda'][1]['Nosaukums']
    match_date = datetime.strptime(json_data['Spele']['Laiks'], '%Y/%m/%d')
    if Match.objects.filter(guest_team__name=guest_team_name, home_team__name=home_team_name, date=match_date).exists() \
            | Match.objects.filter(home_team__name=guest_team_name, guest_team__name=home_team_name, date=match_date).exists():
        raise ValidationError('Match: {guest_team} - {home_team} on {date} is already imported'.format(guest_team=guest_team_name,
                                                                                                       home_team=home_team_name,
                                                                                                       date=match_date.strftime('%d %B, %Y')))
