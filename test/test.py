from flask import session

from body.rooms import Room

room = Room()


class User:
    def __init__(self, role):
        self.role = role


class UserRole:
    def __init__(self, user):
        self.user = user


class RoomMember:
    def __init__(self, role):
        self.role = role


class NonRoomMember:
    def join(self):
        self.u


class RoomMemberRole:
    def __init__(self, room_member):
        self.room_member = room_member

    @property
    def description(self):
        description = {'name': self.__class__.__name__}
        return description

    def leave(self):
        rooms = session.get('rooms', {})
        sess_room = rooms.get(room.id, {})
        sess_room['room_member_role'] = self.description


class TeamMember(RoomMemberRole):
    def __init__(self, room_member, team):
        super().__init__(room_member)
        self.team = team

    def join_spectators(self):
        self.room_member.role = Spectator()


class Spectator(RoomMemberRole):
    def join_team(self, team_id):
        team = room.teams[team_id]
        self.room_member.role = TeamMember(self.room_member, team)


class Speaker(RoomMemberRole):
    def ready(self):
        pass
