from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='match-upload', permanent=False), name='index'),
    path('match/upload', views.upload_match, name='match-upload'),
]
