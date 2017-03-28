#!/usr/bin/python
"""
This file is a part of quicksave project.
Copyright (c) 2016 Aleksander Gajewski <adiog@brainfuck.pl>.
"""

import argparse
import base64
import configparser
import getpass
import json
import os
import pwd
import subprocess
import sys
import tempfile
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def notify(title, message):
    subprocess.call(['notify-send', title, message])


def from_json_string(string):
    if string:
        return base64.b64decode(string.encode('utf-8'))
    else:
        return None


def to_json_string(bytes_array):
    if bytes_array:
        return base64.b64encode(bytes_array).decode('utf-8')
    else:
        return None


class QuicksaveAgent(object):
    config_file = os.path.expanduser('~/.quicksave.cfg')

    def __init__(self):
        self.check_config()
        self.config = configparser.ConfigParser()
        self.config.read([self.config_file])
        self.host = self.get_config('host')
        self.session_id = self.get_config('session_id')
        self.logged_in = False
        self.user = None
        if self.session_id is not None:
            resp = self.json_request('userstate', {})
            if resp.get('result') == 'ok':
                self.user = resp['user']
                self.logged_in = True

    def check_config(self):
        if not os.path.exists(self.config_file):
            cfg = configparser.ConfigParser()
            cfg.add_section('quicksave')
            cfg.set('quicksave', 'host', 'http://quicksave.pl:8080/')
            with open(self.config_file, 'w') as f:
                cfg.write(f)

    def get_config(self, fld, default=None):
        return self.config.get('quicksave', fld, fallback=default)

    def write_config(self, **kwargs):
        for k, v in kwargs.items():
            self.config.set('quicksave', k, v)
            with open(self.config_file, 'w') as f:
                self.config.write(f)

    def json_request(self, relative_url, json_data):
        url = self.host + relative_url
        if '?' not in relative_url:
            url += '/'
        if json_data is not None:
            data = json.dumps(json_data).encode('utf-8')
        else:
            raise ValueError
        headers = {}
        if self.session_id is not None:
            headers['Cookie'] = 'sessionid=' + self.session_id
        headers['Content-Type'] = 'application/json'
        request = Request(url, data=data, headers=headers)
        response = urlopen(request)
        return json.loads(response.read().decode())

    def log_in(self):
        default_login = pwd.getpwuid(os.getuid())[0]
        login = input('Login [%s]: ' % default_login).strip()
        if login == '':
            login = default_login
        password = getpass.getpass('Password: ').strip()
        resp = self.json_request('login', {
            'login': login,
            'password': password,
        })
        if resp.get('result') == 'ok':
            self.user = resp['user']
            self.session_id = resp['session']
            self.write_config(sessionid=self.session_id)
            self.logged_in = True

    def find(self, query):
        url = 'read_many/?' + urlencode({'q': query})
        res = self.json_request(url)
        print(res)
        if res.get('result') == 'ok' and 'items' in res:
            return res['items']
        return []

    def _get_clipboard(self):
        return subprocess.check_output(['xsel', '--clipboard'])

    def take_screenshot(self):
        screenshot = tempfile.mktemp()
        subprocess.check_output(['gnome-screenshot', '--file', screenshot])
        url = 'create'
        with open(screenshot, 'rb') as data_file:
            res = self.json_request(url,
                                    {'content_type': 'application/qs.screenshot',
                                     'title': 'screenshot',
                                     'content': to_json_string(data_file.read())})
        return res

    def sync(self, item_uri):
        if "file://" in item_uri:
            item_uri = item_uri[7:]
        if item_uri[0] == '/':
            local_item_path = item_uri
        else:
            local_item_path = os.path.realpath(item_uri)
        absolute_dir_path = os.path.dirname(local_item_path)
        remote_target_path = '/qs/{}/host/{}/{}'.format(self.user, self.host, absolute_dir_path)
        user_at_host = self.user + '@' + self.host
        mkdir_command = 'mkdir -p {}'.format(remote_target_path)
        subprocess.call(['ssh', user_at_host, mkdir_command])
        subprocess.call(['rsync',
                         '--progress',
                         '--delete',
                         '-avz',
                         '-e', 'ssh',
                         local_item_path,
                         user_at_host + ':' + remote_target_path])
        notify('quicksave.pl', 'Item {} has been saved.'.format(local_item_path))


def quicksave():
    parser = argparse.ArgumentParser(prog='qs')
    subparsers = parser.add_subparsers(help='Available commands', dest='cmd')
    parser_rsync = subparsers.add_parser('rsync', aliases=['r'], help='Sync local item')
    parser_clipboard = subparsers.add_parser('clipboard', aliases=['c'], help='Save content of system clipboard')
    #
    parser_screenshot = subparsers.add_parser('screenshot', aliases=['s'], help='Take screenshot')
    #'--window',
    #'--area',
    #'--delay=SECONDS'
    parser_add = subparsers.add_parser('add', aliases=['a'], help='Add new item')
    parser_add.add_argument('-m', '--comment', type=str, help='Optional note')
    parser_find = subparsers.add_parser('find', aliases=['f'], help='Search through existing items')
    parser_find.add_argument('query', type=str, help='Search query')
    parser_find.add_argument('-s', '--save', type=int, default=-1, metavar='I',
                             help='Save found item locally (provide index from find command without --save)')
    parser_logout = subparsers.add_parser('logout', help='Log out user')

    arg = parser.parse_args(sys.argv[1:])

    qsa = QuicksaveAgent()
    while not qsa.logged_in:
        qsa.log_in()

    if arg.cmd in ('a', 'add'):
        pass
    elif arg.cmd in ('r', 'rsync'):
        pass
    elif arg.cmd in ('c', 'clipboard'):
        pass
    elif arg.cmd in ('s', 'screenshot'):
        qsa.take_screenshot()
    elif arg.cmd in ('f', 'find'):
        items = qsa.find(arg.query)
        if len(items) == 0:
            print('Nothing found')
        else:
            if 0 <= arg.save <= len(items):
                item = items[arg.save - 1]
                if item['item_type'] == 'application/qs.page':
                    subprocess.check_output(['xdg-open', item['source_url']])
                else:
                    print('Saving', item['title'], '...')  # TODO
            else:
                for i in range(min(len(items), 9)):
                    print(str(i + 1) + '.', items[i]['title'])
                if len(items) > 9:
                    print('\nMore items available. Provide more precise query to find them.')
    elif arg.cmd == 'logout':
        pass


if __name__ == '__main__':
    quicksave()
