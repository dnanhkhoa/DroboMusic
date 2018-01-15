#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import os
import pickle

import logone
import requests
from requests import RequestException

_APP_PATH = os.path.normpath(os.path.dirname(os.path.abspath(__file__)))
_LOGGER = logone.get_logger(__name__)


def path(*name):
    assert name is not None, 'Name is invalid!'
    return os.path.join(_APP_PATH, *name)


def path_info(name):
    assert name is not None, 'Name is invalid!'
    name = path(name)
    if len(name) > 0 and os.path.exists(name):
        if os.path.isfile(name):
            return 1
        if os.path.isdir(name):
            return -1
    return 0


def make_dirs(name):
    assert name is not None, 'Name is invalid!'
    name = path(name)
    if len(name) > 0 and path_info(name) >= 0:
        os.makedirs(name)


def read_file(file_name):
    file_name = path(file_name)
    assert path_info(file_name) == 1, 'File do not exist!'
    with open(file_name, 'rb') as f:
        try:
            return f.read().decode('UTF-8')
        except Exception as e:
            _LOGGER.exception(e)


def write_file(data, file_name):
    file_name = path(file_name)
    make_dirs(os.path.dirname(file_name))
    with open(file_name, 'wb') as f:
        try:
            f.write(data.encode('UTF-8'))
        except Exception as e:
            _LOGGER.exception(e)


def read_bytes(file_name):
    file_name = path(file_name)
    assert path_info(file_name) == 1, 'File do not exist!'
    with open(file_name, 'rb') as f:
        try:
            return f.read()
        except Exception as e:
            _LOGGER.exception(e)


def write_bytes(data, file_name):
    file_name = path(file_name)
    make_dirs(os.path.dirname(file_name))
    with open(file_name, 'wb') as f:
        try:
            f.write(data)
        except Exception as e:
            _LOGGER.exception(e)


def serialize(obj, file_name):
    file_name = path(file_name)
    make_dirs(os.path.dirname(file_name))
    with open(file_name, 'wb') as f:
        try:
            pickle.dump(obj, f)
        except Exception as e:
            _LOGGER.exception(e)


def deserialize(file_name):
    file_name = path(file_name)
    assert path_info(file_name) == 1, 'File do not exist!'
    with open(file_name, 'rb') as f:
        try:
            return pickle.load(f)
        except Exception as e:
            _LOGGER.exception(e)


def read_lines(file_name):
    file_name = path(file_name)
    assert path_info(file_name) == 1, 'File do not exist!'
    lines = []
    with open(file_name, 'rb') as f:
        try:
            for line in f:
                lines.append(line.decode('UTF-8').rstrip('\r\n'))
        except Exception as e:
            _LOGGER.exception(e)
    return lines


def write_lines(lines, file_name, end_line='\n'):
    file_name = path(file_name)
    make_dirs(os.path.dirname(file_name))
    with open(file_name, 'wb') as f:
        try:
            for line in lines:
                f.write((line + end_line).encode('UTF-8'))
        except Exception as e:
            _LOGGER.exception(e)


def read_json(file_name):
    file_name = path(file_name)
    assert path_info(file_name) == 1, 'File do not exist!'
    with open(file_name, 'rb') as f:
        try:
            return json.loads(f.read().decode('UTF-8'))
        except Exception as e:
            _LOGGER.exception(e)


def write_json(obj, file_name):
    file_name = path(file_name)
    make_dirs(os.path.dirname(file_name))
    with open(file_name, 'wb') as f:
        try:
            f.write(json.dumps(obj, indent=4, ensure_ascii=False).encode('UTF-8'))
        except Exception as e:
            _LOGGER.exception(e)


def download_file(url, file_name=None):
    assert url is not None, 'URL is invalid!'
    try:
        response = requests.get(url=url, allow_redirects=True)
        if response.status_code == requests.codes.ok:
            content = response.content
            if file_name is None:
                return content
            write_bytes(content, file_name)
    except RequestException as e:
        _LOGGER.exception(e)
    return None
