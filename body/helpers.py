import os
import random
import string
from flask import url_for


class URL:
    @staticmethod
    def for_static(*path):
        return url_for('static', filename=os.path.join(*path))

    @staticmethod
    def for_img(filename):
        return URL.for_static('img', filename)

    @staticmethod
    def for_css(filename):
        return URL.for_static('css', filename)

    @staticmethod
    def for_js(filename):
        return URL.for_static('js', filename)

    @staticmethod
    def for_pfp(filename):
        return url_for('pfp', filename=filename)


def get_random_string(k=20):
    return ''.join(random.choices(string.ascii_letters, k=k))


def get_random_color():
    return [random.randint(0, 255) for _ in range(3)]


def get_extension(file):
    if '.' in file.filename:
        return file.filename.rsplit('.', 1)[1].lower()


post_get = dict(methods=['POST', 'GET'])
