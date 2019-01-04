import json

from django.forms import forms, ClearableFileInput

from football_app.apps.football.validators import match_json_validator


class MatchForm(forms.Form):
    match_json_file = forms.FileField(
        label='Match data in JSON format',
        required=True,
        widget=ClearableFileInput(attrs={'class': 'form-control-file', 'accept': '.json,application/json', 'multiple': True})
    )

    def clean_match_json_file(self):
        match_json_file_list = self.files.getlist('match_json_file')
        match_json_list = list(map(lambda file: json.load(file.open('r')), match_json_file_list))

        for match_json in match_json_list:
            match_json_validator(match_json)

        return match_json_list
