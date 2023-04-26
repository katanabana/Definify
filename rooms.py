import datetime
import itertools
import time
from threading import Thread

from flask_login import current_user
from flask_socketio import join_room, emit

from helpers import *


def user():
    return current_user._get_current_object()


class Team:
    def __init__(self, name):
        self.color = get_random_color()
        self.members = []
        self.score = 0
        self.name = name
        self.id = get_random_string()

    def add(self):
        self.members.append(user())

    def user_is_in(self):
        return user() in self.members

    def remove_user(self):
        self.members.remove(user())

    def __iter__(self):
        return self.members.__iter__()


class Room:
    @classmethod
    @property
    def event_handlers(cls):
        return cls.create_team, cls.join, cls.move_to_team, cls.move_to_spectators, cls.start, cls.play, cls.pause

    def __init__(self):
        self.id = get_random_string()
        self.teams = []
        self.started = False
        self.running = False
        self.speaking = False
        self.spectators = []
        self.master = user()

    def emit(self, event_name, data=()):
        emit(event_name, data, to=self.id)

    def create_team(self):
        team = Team(f'Team {len(self.teams) + 1}')
        self.teams.append(team)
        self.emit('create_team', (team.id, team.name))

    def move_to_team(self, team_id):
        for team in self.teams:
            if team.id == team_id:
                if user() in self.spectators:
                    self.spectators.remove(user())
                team.add()
        self.emit('move_to_team', (current_user.id, team_id))

    def join(self):
        if not self.user_is_in():
            self.spectators.append(user())
            join_room(self.id)
            self.emit('join', (current_user.id, current_user.nickname, self.user_is_master(), current_user.pfp))

    def move_to_spectators(self):
        for team in self.teams:
            if team.user_is_in():
                team.remove_user()
                break
        if user() not in self.spectators:
            self.join()
        self.emit('move_to_spectators', current_user.get_id())

    def start(self):
        self.started = True
        self.running = True
        self.emit('start')
        self.emit('count_down', 90)

    def play(self):
        self.running = True
        self.emit('play')

    def pause(self):
        self.running = False
        self.emit('pause')


    def get_all_users(self):
        return list(itertools.chain(self.spectators, *[team.members for team in self.teams]))

    def user_is_in(self):
        return user() in self.get_all_users()

    def user_is_master(self):
        return user() == self.master


class WaitThread(Thread):
    def __init__(self, stage):
        def target():
            time.sleep(stage.time_left)
            stage.end()

        super().__init__(target=target)


class FiniteStage:
    max_time = datetime.time(minute=1)

    def __init__(self):
        self.time_left = self.max_time
        self.thread = WaitThread(self)
        self.thread.start()
        self.start_time = datetime.datetime.now()

    def stop(self):
        self.thread.join()
        self.time_left -= datetime.datetime.now() - self.start_time

    def resume(self):
        self.thread = WaitThread(self.time_left)

    def end(self):
        self.time_left = None
