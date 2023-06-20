from flask_login import current_user


class Descriptor:
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        return self.func()


class Current:
    user = current_user._get_current_object()
