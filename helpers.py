import datetime
import os
import random
import string
from flask import url_for, session

from constants import UPLOAD_FOLDER, NAME


def url_for_static(*path):
    return url_for('static', filename="/".join(path))


def url_for_img(filename):
    return url_for_static('img', filename)


def url_for_css(filename):
    return url_for_static('css', filename)


def url_for_js(filename):
    return url_for_static('js', filename)


def get_params(additional_params=None, **kwargs):
    # common params are those that are often used in templates
    # to avoid adding them to every params dict they are automatically added by this function
    # if additional params weren't passed only common params are returned
    if additional_params is None:
        additional_params = {}
    common_params = {
        'url_for_img': url_for_img,
        'url_for_css': url_for_css,
        'url_for_js': url_for_js,
        'NAME': NAME
    }
    return {**common_params, **additional_params, **kwargs}



def get_random_string(k=20):
    return ''.join(random.choices(string.ascii_letters, k=k))


def get_random_color():
    return [random.randint(0, 255) for _ in range(3)]


def pfp_exists(pfp):
    return os.path.exists(get_path_to_pfp(pfp))


def get_path_to_pfp(pfp_url):
    return os.path.join(UPLOAD_FOLDER, pfp_url[1:])


def get_extension(file):
    if '.' in file.filename:
        return file.filename.rsplit('.', 1)[1].lower()