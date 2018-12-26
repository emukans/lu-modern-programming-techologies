from django.db import models


class Stadium(models.Model):
    name: str = models.CharField(max_length=50)


class Team(models.Model):
    name: str = models.CharField(max_length=50)


class Player(models.Model):
    ROLE_CHOICES = (
        ('V', 'GOALKEEPER'),
        ('A', 'DEFENDER'),
        ('U', 'FORWARD')
    )

    first_name: str = models.CharField(max_length=50)
    last_name: str = models.CharField(max_length=50)
    number: int = models.IntegerField()
    role: str = models.CharField(max_length=1, choices=ROLE_CHOICES)
    team: Team = models.ForeignKey(Team, on_delete=models.CASCADE)


class Referee(models.Model):
    first_name: str = models.CharField(max_length=50)
    last_name: str = models.CharField(max_length=50)
