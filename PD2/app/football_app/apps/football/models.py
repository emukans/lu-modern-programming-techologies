from django.db import models
import datetime


class Stadium(models.Model):
    name: str = models.CharField(max_length=50)


class Team(models.Model):
    name: str = models.CharField(max_length=50)


class Player(models.Model):
    GOALKEEPER = 'V'
    DEFENDER = 'A'
    FORWARD = 'U'

    ROLE_CHOICES = (
        (GOALKEEPER, 'GOALKEEPER'),
        (DEFENDER, 'DEFENDER'),
        (FORWARD, 'FORWARD')
    )

    first_name: str = models.CharField(max_length=50)
    last_name: str = models.CharField(max_length=50)
    number: int = models.IntegerField()
    role: str = models.CharField(max_length=1, choices=ROLE_CHOICES)
    team: Team = models.ForeignKey(Team, on_delete=models.CASCADE)


class Referee(models.Model):
    first_name: str = models.CharField(max_length=50)
    last_name: str = models.CharField(max_length=50)


class Match(models.Model):
    date: datetime.date = models.DateField(blank=True, null=True)
    viewers: int = models.IntegerField(blank=True, null=True)
    stadium: Stadium = models.ForeignKey(Stadium, on_delete=models.CASCADE)
    home_team: Team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='%(class)s_home_team')
    guest_team: Team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='%(class)s_guest_team')
    main_referee: Referee = models.ForeignKey(Referee, on_delete=models.CASCADE, related_name='%(class)s_main_referee', blank=True, null=True)
    line_referee = models.ManyToManyField(Referee, related_name='%(class)s_line_referee')


class BaseTeamOnMatch(models.Model):
    match: Match = models.ForeignKey(Match, on_delete=models.CASCADE)
    team: Team = models.ForeignKey(Team, on_delete=models.CASCADE)
    base_players = models.ManyToManyField(Player)


class Foul(models.Model):
    match: Match = models.ForeignKey(Match, on_delete=models.CASCADE)
    minute: int = models.IntegerField()
    second: int = models.IntegerField()
    player: Player = models.ForeignKey(Player, on_delete=models.CASCADE)


class Change(models.Model):
    replaced_from: Player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='%(class)s_replaced_from')
    replaced_to: Player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='%(class)s_replaced_to')
    minute: int = models.IntegerField()
    second: int = models.IntegerField()
    match: Match = models.ForeignKey(Match, on_delete=models.CASCADE)


class Goal(models.Model):
    GOAL_TYPE = (
        ('J', 'PENALTY'),
        ('N', 'FROM_GAME')
    )
    match: Match = models.ForeignKey(Match, on_delete=models.CASCADE)
    minute: int = models.IntegerField()
    second: int = models.IntegerField()
    player: Player = models.ForeignKey(Player, on_delete=models.CASCADE)
    goal_type: str = models.CharField(max_length=1, choices=GOAL_TYPE)


class GoalCombination(models.Model):
    goal: Goal = models.ForeignKey(Goal, on_delete=models.CASCADE)
    participated_players = models.ManyToManyField(Player)
