import json

from django.core.exceptions import ValidationError
from django.forms import forms, ClearableFileInput


class MatchForm(forms.Form):
    match_json_file = forms.FileField(
        label='Match data in JSON format',
        required=True,
        widget=ClearableFileInput(attrs={'class': 'form-control-file', 'accept': '.json,application/json', 'multiple': True})
    )

    def clean_match_json_file(self):
        match_json_file_list = self.files.getlist('match_json_file')
        # Validate file
        # raise ValidationError()

        return list(map(lambda file: json.load(file.open('r')), match_json_file_list))
