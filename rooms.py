import datetime
import itertools
import time
from random import choice
from threading import Thread

from flask_login import current_user
from flask_socketio import join_room, emit, leave_room

from api import get_random_word
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

    def add_user(self):
        self.members.append(user())

    def user_is_in(self):
        return user() in self.members

    def remove_user(self):
        if user() in self.members:
            self.members.remove(user())

    def __iter__(self):
        return self.members.__iter__()

    def __bool__(self):
        return bool(self.members)


class Room:
    @classmethod
    @property
    def event_handlers(cls):
        return cls.create_team, cls.join, cls.move_to_team, cls.move_to_spectators, cls.start, cls.speak, cls.guess, cls.leave

    def __init__(self, socketio):
        self.id = get_random_string()
        self.teams = []
        self.started = False
        self.ended = False
        self.running = False
        self.speaking = False
        self.stage = None
        self.speaker = None
        self.current_team_index = None
        self.spectators = []
        self.master = user()
        self.socketio = socketio
        self.word = None
        self.win_score = 10
        self.speak_time = 30

    def emit(self, event_name, data=()):
        emit(event_name, data, to=self.id)

    def create_team(self):
        for team in self.teams:
            if team.user_is_in() and len(team.members) == 1:
                return
        self.remove_user()
        team = Team(f'Team {len(self.teams) + 1}')
        team.add_user()
        self.teams.append(team)
        self.emit('create_team', (current_user.id, team.id, team.name))

    def move_to_team(self, team_id):
        for team in self.teams:
            if team.user_is_in() and team.id == team_id:
                return
        self.remove_user()
        for team in self.teams:
            if team.id == team_id:
                team.add_user()
                break
        self.emit('move_to_team', (current_user.id, team_id))

    def join(self):
        if not self.user_is_in():
            new_user = user()
            new_user.score = 0
            join_room(self.id)
            join_room(current_user.id)
            self.emit('join', (current_user.id, current_user.nickname, current_user.pfp))
            self.spectators.append(new_user)

    def remove_user(self):
        teams = []
        for team in self.teams:
            team.remove_user()
            if team.members:
                teams.append(team)
        if user() in self.spectators:
            self.spectators.remove(user())
        self.teams = teams

    def move_to_spectators(self):
        if user() not in self.spectators:
            self.remove_user()
            self.spectators.append(user())
            self.emit('move_to_spectators', current_user.get_id())

    def start(self):
        if self.teams and all(map(lambda team: len(team.members) > 1, self.teams)):
            self.started = True
            self.running = True
            self.current_team_index = 0
            self.emit('start')
            self.stage = Waiting(self)

    def get_all_users(self):
        return list(itertools.chain(self.spectators, *[team.members for team in self.teams]))

    def user_is_in(self):
        return user() in self.get_all_users()

    def user_is_master(self):
        return user() == self.master

    def speak(self):
        self.stage.next()

    def next_team(self):
        self.current_team_index = (self.current_team_index + 1) % len(self.teams)

    def guess(self, guess):
        if user() in self.teams[self.current_team_index] and user() != self.speaker:
            correct = guess.strip().lower() == self.word
            self.emit('guess', (current_user.id, guess, correct))
            if correct:
                self.word = get_random_word()
                self.teams[self.current_team_index].score += 1
                current_user.score += 1
                self.speaker.score += 1
                self.teams[self.current_team_index].score += 2
                if self.teams[self.current_team_index].score >= self.win_score:
                    self.ended = True
                    self.emit('end', self.teams[self.current_team_index].id)

    def leave(self):
        leave_room(self.id)
        self.emit('leave', current_user.id)
        for team in self.teams:
            if team.user_is_in():
                team.remove_user()
                break
        else:
            self.spectators.remove(user())


class SleepTemporaryThread(Thread):
    def __init__(self, stage):
        def target():
            time.sleep(stage.time_left.seconds)
            stage.end()

        super().__init__(target=target)


class SleepForeverThread(Thread):
    def __init__(self, _):
        def pass_():
            while True:
                pass

        super().__init__(target=pass_)


class Stage:
    next_stage = None
    thread_type = None

    def __init__(self, room):
        self.room = room
        self.thread = self.thread_type(self)
        self.thread.start()

    def next(self):
        self.room.stage = self.next_stage(self.room)

    def emit(self, event_name, data=()):
        self.room.socketio.emit(event_name, data, room=self.room.id, namespace='/match/<id_>')


class InfiniteStage(Stage):
    thread_type = SleepForeverThread


class FiniteStage(Stage):
    max_time = datetime.timedelta(seconds=Room(None).speak_time)
    thread_type = SleepTemporaryThread

    def __init__(self, room):
        self.time_left = self.max_time
        self.start_time = datetime.datetime.now()
        super().__init__(room)
        self.emit('count_down', self.max_time.seconds)

    def end(self):
        self.next()


class Waiting(InfiniteStage):
    max_time = datetime.timedelta(seconds=5)

    def __init__(self, room):
        super().__init__(room)
        self.room.next_team()
        members = [i for i in self.room.teams[self.room.current_team_index].members if self.room.speaker is None or self.room.speaker != i]
        self.room.speaker = choice(members)
        self.emit('wait', room.speaker.id)


class Speaking(FiniteStage):
    def __init__(self, room):
        super().__init__(room)
        self.emit('speak')
        self.room.word = get_random_word()
        self.room.socketio.emit('update_word', self.room.word, room=self.room.speaker.id, namespace='/match/<id_>')


Waiting.next_stage = Speaking
Speaking.next_stage = Waiting
