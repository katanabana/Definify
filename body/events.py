from flask_socketio import SocketIO, Namespace

from body.current import Current
from rooms import Room
from global_ import rooms


class MySocketIO(SocketIO):
    def on_room_event(self, room_method):
        def handler(data):
            room_id, args = data[0], data[1:]
            if room_id in rooms:
                room_method(rooms[room_id], *args)

        self.on_event(room_method.__name__, handler, namespace='/match/<id_>')


class RoomEventRegistrator:
    def __init__(self, socketio, namespace):
        self.socketio = socketio
        self.namespace = namespace

    def register(self, event):
        self.socketio.on_event(event.__name__, lambda data: Current.room.event(*data), namespace=self.namespace)


def connect_to_events(app):
    socketio = MySocketIO(app)
    for method in Room.event_handlers:
        socketio.on_room_event(method)
    return socketio