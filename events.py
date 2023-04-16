from flask import render_template, redirect
from public import current_user
from flask_socketio import Namespace, emit, SocketIO


from rooms import Room
from global_ import rooms


class MatchNamespace(Namespace):
    def on_create_team(self, room_id):
        if room_id in rooms:
            id_ = rooms[room_id].create_team()
            emit('create_team', id_, broadcast=True)

    def on_join(self, room_id):
        if room_id in rooms and current_user not in rooms[room_id]:
            rooms[room_id].join(current_user)
            emit('join', (current_user.nickname, current_user.get_id()), broadcast=True)

    def on_move_to_team(self, data):
        room_id, team_id = data
        if room_id in rooms:
            rooms[room_id].move_to_team(current_user, team_id)
            emit('move_to_team', (current_user.get_id(), team_id), broadcast=True)

    def on_move_to_spectators(self, room_id):
        if room_id in rooms:
            rooms[room_id].move_to_spectators(current_user)
            emit('move_to_spectators', (current_user.get_id()), broadcast=True)


def connect_to_events(app):
    socketio = SocketIO(app)
    socketio.on_namespace(MatchNamespace('/match/<id>'))
    return socketio
