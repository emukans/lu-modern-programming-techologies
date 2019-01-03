import json

from django.http import HttpRequest
from django.shortcuts import render

from football_app.apps.football.forms import MatchForm
from football_app.apps.football.parser.match_json_parser import match_json_parser


def upload_match(request: HttpRequest):
    form = MatchForm()
    is_upload_successful = False

    if request.method == 'POST':
        form = MatchForm(request.POST, request.FILES)

        if form.is_valid():
            match_json_parser(form.cleaned_data.get('match_json_file'))
            is_upload_successful = True

    return render(request, 'football_app/match/upload.html', {'form': form, 'is_upload_successful': is_upload_successful})
