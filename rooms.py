import itertools

from helpers import *
from flask_login import current_user



class Team:
    def __init__(self, name):
        self.color = get_random_color()
        self.members = []
        self.score = 0
        self.name = name
        self.id = get_random_string()

    def add(self, user):
        self.members.append(user)

    def __contains__(self, user):
        return user in self.members

    def remove(self, user):
        self.members.remove(user)

    def __iter__(self):
        iter(self.members)

    @property
    def member_nicknames(self):
        return [member.nickname for member in self.members]


class Room:
    def __init__(self):
        self.id = get_random_string()
        self.teams = []
        self.started = False
        self.running = False
        self.speaking = False
        self.spectators = [current_user]
        self.master = current_user

    def create_team(self):
        team = Team(f'Team {len(self.teams) + 1}')
        self.teams.append(team)
        return team.id

    def move_to_team(self, user, team_id):
        for team in self.teams:
            if team.id == team_id:
                if user in self.spectators:
                    self.spectators.remove(user)
                for team in self.teams:
                    if user in team:
                        team.remove(user)
                team.add(user)

    def join(self, user):
        if user not in self.get_all_users():
            self.spectators.append(user)

    def move_to_spectators(self, user):
        for team in self.teams:
            if user in team:
                team.remove(user)
                break
        self.spectators.append(user)

    def get_all_users(self):
        return list(itertools.chain(self.spectators, *[team.members for team in self.teams]))

    def __contains__(self, user):
        return user in self.get_all_users()
