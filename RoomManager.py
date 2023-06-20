from body.rooms import Room


class RoomManager:
    id_counter = 0

    def __init__(self):
        self.rooms = {}

    def create_new_room(self):
        RoomManager.id_counter += 1
        room_id = RoomManager.id_counter
        new_room = Room(room_id)
        self.rooms[room_id] = new_room
        return new_room
