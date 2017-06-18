# This file is a part of quicksave project.
# Copyright (c) 2017 Aleksander Gajewski <adiog@quicksave.io>

import configparser
import getpass
import json
import os

import requests

SESSION_COOKIE_NAME = 'token'


def get_api_url():
    return API.config['API']['url']


def get_cdn_url():
    return API.config['CDN']['url']


def get_oauth_url():
    return API.config['OAUTH']['url']


def read_token(token_file):
    with open(token_file, 'r') as f:
        return f.read()


def set_token(token_file, token):
    with open(token_file, 'w') as f:
        f.write(token)


def get_token(username, password):
    response = requests.post(get_oauth_url() + '/token/get', auth=(username, password), data=json.dumps({'expireTime': 3600}), verify=False)
    if response.status_code == 200:
        token = json.loads(response.text)['token']
        requests.post(get_api_url() + '/token/put', data=json.dumps({'token': token}), verify=False)
        return token
    else:
        return ''


def cookie_requests_get(cookie, *args, **kwargs):
    return requests.get(*args, **kwargs, cookies={SESSION_COOKIE_NAME: cookie}, verify=False)


def cookie_requests_post(cookie, *args, **kwargs):
    return requests.post(*args, **kwargs, cookies={SESSION_COOKIE_NAME: cookie}, verify=False)


def cookie_requests_post_json(cookie, *args, **kwargs):
    response = cookie_requests_post(cookie, *args, **kwargs)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        print(response)
        raise RuntimeError()


def is_token_valid(token):
    response = cookie_requests_get(token, get_api_url() + '/session/check')
    return response.status_code == 200


class CookieAuthentication(object):
    def __enter__(self):
        token = read_token(API.token_file)
        if not is_token_valid(token):
            if API.credentials and API.credentials[0]:
                username = API.credentials[0]
                if API.credentials[1]:
                    password = API.credentials[1]
                else:
                    password = getpass.getpass('Password: ')
                token = get_token(username, password)
            while not is_token_valid(token):
                username = input('Username [%s]: ' % getpass.getuser())
                if username == '':
                    username = getpass.getuser()
                password = getpass.getpass('Password: ')
                token = get_token(username, password)
            else:
                set_token(API.token_file, token)
        return token

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class API(object):
    config = None
    token_file = None
    credentials = None

    @classmethod
    def post(cls, url, json):
        with CookieAuthentication() as token:
            return cookie_requests_post_json(token, get_api_url() + url, data=json)

    @classmethod
    def upload(cls, meta_hash, mimetype, filename, filebase):
        with CookieAuthentication() as token:
            return cookie_requests_post_json(token, get_api_url() + '/upload', data=json.dumps({'meta_hash': meta_hash, 'mimetype': mimetype, 'filename': filename, 'filebase': filebase}))

    @classmethod
    def create(cls, meta): #, meta_type, name, text, source_url, source_title):
        createRequestBean = {'meta': meta} #{'meta_type': meta_type, 'name': name, 'text': text, 'source_url': source_url, 'source_title': source_title}}
        with CookieAuthentication() as token:
            return cookie_requests_post_json(token, get_api_url() + '/create', data=json.dumps(createRequestBean))

    @classmethod
    def tag_create(cls, meta_hash, tag_name_value):
        split_tag_name_value = tag_name_value.split('#')
        name = split_tag_name_value[0]
        if len(split_tag_name_value) > 1:
            value = '#'.join(split_tag_name_value[1:])
        else:
            value = ''
        tag = {
            'meta_hash': meta_hash,
            'name': name,
            'value': value
        }
        with CookieAuthentication() as token:
            return cookie_requests_post_json(token, get_api_url() + '/tag/create', data=json.dumps({'tag': tag}))


class CDN(object):
    @classmethod
    def get(cls, url):
        with CookieAuthentication() as token:
            return cookie_requests_get(token, get_cdn_url() + url)
