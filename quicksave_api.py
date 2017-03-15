# This file is a part of quicksave project.
# Copyright (c) 2017 Aleksander Gajewski <adiog@quicksave.io>

import configparser
import getpass
import json
import os

import requests

SESSION_COOKIE_NAME = 'sessionid'


class Config(object):
    config = None
    config_filepath = 'quicksave.ini'

    @classmethod
    def get_default(cls):
        default_config = configparser.ConfigParser()
        default_config['API']['url'] = os.environ.get('IO_QUICKSAVE_API', 'https://api.quicksave.io')
        default_config['USER']['token'] = ''
        return default_config

    @classmethod
    def get_config(cls):
        if Config.config is None:
            Config.config = configparser.ConfigParser()
            if not Config.config.read(Config.config_filepath):
                Config.config = Config.get_default()
        return Config.config

    @classmethod
    def get_api_url(cls):
        return Config.get_config()['API']['url']

    @classmethod
    def get_token(cls):
        return Config.get_config()['USER']['token']

    @classmethod
    def set_token(cls, token):
        Config.config['USER']['token'] = token
        with open(Config.config_filepath, 'w') as config_file:
            Config.config.write(config_file)


def get_cookie(username, password):
    response = requests.post(Config.get_api_url() + '/login/', auth=(username, password), data={}, verify=False)
    if response.status_code == 200:
        return response.cookies.get(SESSION_COOKIE_NAME)
    else:
        return ''


def cookie_requests_post(cookie, *args, **kwargs):
    return requests.post(*args, **kwargs, cookies={SESSION_COOKIE_NAME: cookie}, verify=False)


def is_token_valid(token):
    response = cookie_requests_post(token, Config.get_api_url() + '/status/')
    return response.status_code == 200


class CookieAuthentication(object):
    def __enter__(self):
        token = Config.get_token()
        while not is_token_valid(token):
            username = input('Username [%s]: ' % getpass.getuser())
            if username == '':
                username = getpass.getuser()
            password = getpass.getpass('Password: ')
            token = get_cookie(username, password)
        else:
            Config.set_token(token)
        return token

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class API(object):
    @classmethod
    def upload(cls, item_id, filename, filebase):
        with CookieAuthentication() as token:
            cookie_requests_post(token, Config.get_api_url() + '/upload/', data=json.dumps({'item_id': item_id, 'filename': filename, 'filebase': filebase}))
