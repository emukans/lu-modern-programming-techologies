import json

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.forms import forms, ClearableFileInput


class MatchForm(forms.Form):
    match_json_file = forms.FileField(
        label='Match data in JSON format',
        required=True,
        widget=ClearableFileInput(attrs={'class': 'form-control-file', 'accept': '.json,application/json'})
    )

    def clean_match_json_file(self):
        match_json_file = self.cleaned_data.get('match_json_file')  # type: InMemoryUploadedFile
        # Validate file
        # raise ValidationError()

        return json.load(match_json_file.open('r'))
