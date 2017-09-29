#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This file is a part of quicksave project.
Copyright (c) 2017 Aleksander Gajewski <adiog@quicksave.io>.
"""
import base64
import configparser
import json
import os
import subprocess
import tempfile
from os.path import expanduser
import argparse

import re

import sys
from magic import Magic

from cliCredentialsPrompt import cli_credentials_prompt
from guiCredentialsPrompt import gui_credentials_prompt
from quicksave_api import API, CookieAuthentication

meta_override_arguments = ['icon', 'name', 'text', 'author', 'source_url', 'source_title']

class GLOBAL(object):
    dry = False


def get_parsed_override_meta(args):
    override_meta = {}
    for meta_attr in meta_override_arguments:
        args_attr = 'set_' + meta_attr
        if getattr(args, args_attr):
            override_meta[meta_attr] = getattr(args, args_attr)
    return override_meta


def get_config_for_option(config, override_meta, option):
    common_meta = dict(config['default'])
    #print(common_meta)
    config_meta = dict(config['%s' % option])
    #print(config_meta)
    command = config_meta.pop('cmd')
    common_meta.update(config_meta)

    filename = tempfile.NamedTemporaryFile().name

    bashed_meta = {k:subprocess.getoutput('echo \'echo "%s"\' | bash' % v) for k,v in common_meta.items()}
    command = re.sub('\$\{QUICKSAVE_OUTPUT_FILE\}', filename, command)
    #print(command)
    #print(bashed_meta)
    #print(override_meta)
    bashed_meta.update(override_meta)
    #print(bashed_meta)
    return command, filename, bashed_meta

def qs():
    parser = argparse.ArgumentParser()

    parser.add_argument("-C", "--config-file", help="use config file [default ~/.quicksave.ini]")
    parser.add_argument("-K", "--token-file", help="use token file [default ~/.quicksave.token]")

    prompt_group = parser.add_mutually_exclusive_group(required=False)
    prompt_group.add_argument("--gui", dest="gui", help="use GUI prompt", action='store_true')
    prompt_group.add_argument("--cli", dest="cli", help="use CLI prompt", action='store_true')
    prompt_group.add_argument("--inline", dest="inline", help="use provided credentials", action='store_true')

    parser.add_argument("-U", "--username", help="authenticate with username", action="store_true")
    parser.add_argument("-P", "--password", help="authenticate with password [unsafe!]", action="store_true")

    #parser.add_argument("-q", "--query", help="retrieve items by QSQL query")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-s", "--screenshot", help="quicksave screenshot", action="store_true")
    group.add_argument("-a", "--area", help="quicksave screenshot with area picker", action="store_true")
    group.add_argument("-f", "--file", help="quicksave file")
    group.add_argument("-c", "--clipboard", help="quicksave current clipboard content", action="store_true")
    group.add_argument("-t", "--text", help="quciksave text")
    group.add_argument("-i", "--input", help="quicksave text with external editor", action="store_true")
    group.add_argument("-D", "--dev", help="developer mode")

    parser.add_argument('-T', '--add-tag', action='append', nargs=1, metavar=('TAG'))
    parser.add_argument("-d", "--dry", help="dry run", action="store_true")


    setter_group = parser.add_argument_group()
    for meta_attr in meta_override_arguments:
        setter_group.add_argument("--set-" + meta_attr, metavar=meta_attr.upper(), help="override default " + meta_attr)

    args = parser.parse_args()

    home = expanduser("~")

    prompt = cli_credentials_prompt
    if args.cli:
        CookieAuthentication.prompt = cli_credentials_prompt
    elif args.gui:
        CookieAuthentication.prompt = gui_credentials_prompt

    if args.config_file:
        config_file = args.config_file
    else:
        config_file = home + '/.quicksave.ini'

    if args.token_file:
        token_file = args.token_file
    else:
        token_file = home + '/.quicksave.token'

    GLOBAL.dry = args.dry

    config = configparser.ConfigParser()
    config.read(config_file)

    if args.inline:
        if args.username:
            username = args.username
        else:
            username = None
        if args.password:
            password = args.password
        else:
            password = None
        credentials = (username, password)
    else:
        credentials = None

    API.credentials = credentials
    API.config = config
    API.token_file = token_file

    override_meta = get_parsed_override_meta(args)

    meta_hash = ''

    if args.dev:
        [url, data] = args.dev.split('?')
        print(url)
        print(data)
        API.dev(url, data)
        sys.exit(0)

    try:
        if args.screenshot:
            mata_hash = screenshot(config, override_meta)
        elif args.area:
            meta_hash = area(config, override_meta)
        elif args.file:
            meta_hash = file(config, override_meta, args.file)
        elif args.clipboard:
            meta_hash = clipboard(config, override_meta)
        elif args.text:
            meta_hash = text(config, override_meta, args.text)
        elif args.input:
            meta_hash = do_input(config, override_meta)
        else:
            print("just getting token")
    except KeyboardInterrupt:
        if config['GUI']['notify_failure_cmd']:
            notify = 'Failure'
            subprocess.check_output([re.sub('\$\{NOTIFICATION\}', notify, part) for part in config['GUI']['notify_failure_cmd'].split(' ')])
    else:
        if meta_hash and args.add_tag:
            for tag in args.add_tag:
                API.tag_create(meta_hash, tag[0])



def screenshot(config, override_meta):
    print("screenhot")
    cmd, cmd_output, meta = get_config_for_option(config, override_meta, 'screenshot')
    print(cmd)
    print(subprocess.check_output(cmd.split(' ')))
    meta.update({'meta_type': 'quicksave/screenshot'})
    if not GLOBAL.dry:
        response = API.create(meta)
        meta_hash = response['item']['meta']['meta_hash']
    else:
        print('API.create(%s)' % meta)
        meta_hash = ''
    magic_mimetyper = Magic()
    mimetype = magic_mimetyper.from_file(cmd_output)
    with open(cmd_output, 'rb') as file:
        filebase = base64.b64encode(file.read()).decode('ascii')
        filename = 'screenshot.png'
        if not GLOBAL.dry:
            API.upload(meta_hash, mimetype, filename, filebase)
        else:
            print('API.upload(__meta_hash__, %s, %s, __base64__)' % (mimetype, filename))
    return meta_hash

def area(config, override_meta):
    print("area")
    cmd, cmd_output, meta = get_config_for_option(config, override_meta, 'area')
    print(cmd)
    print(subprocess.check_output(cmd.split(' ')))
    meta.update({'meta_type': 'quicksave/screenshot'})
    if not GLOBAL.dry:
        response = API.create(meta)
        meta_hash = response['item']['meta']['meta_hash']
    else:
        print('API.create(%s)' % meta)
        meta_hash = ''
    magic_mimetyper = Magic()
    mimetype = magic_mimetyper.from_file(cmd_output)
    with open(cmd_output, 'rb') as file:
        filebase = base64.b64encode(file.read()).decode('ascii')
        filename = 'screenshot.png'
        if not GLOBAL.dry:
            API.upload(meta_hash, mimetype, filename, filebase)
        else:
            print('API.upload(__meta_hash__, %s, %s, __base64__)' % (mimetype, filename))
    return meta_hash

def file(config, override_meta, upload_file):
    print("file")

    common_meta = dict(config['default'])
    bashed_meta = {k:subprocess.getoutput('echo \'echo "%s"\' | bash' % v) for k,v in common_meta.items()}
    bashed_meta.update(override_meta)

    magic_mimetyper = Magic()
    mimetype = magic_mimetyper.from_file(upload_file)

    meta = bashed_meta

    meta_type = 'file'
    for autodetect_group in config['autodetect']:
        autodetect_patterns = json.loads(config['autodetect'][autodetect_group])
        for autodetect_pattern in autodetect_patterns:
            print(autodetect_pattern, mimetype)
            if mimetype == autodetect_pattern:
                meta_type = autodetect_group
    meta.update({'meta_type': 'quicksave/' + meta_type})
    if not GLOBAL.dry:
        response = API.create(meta)
        meta_hash = response['item']['meta']['meta_hash']
    else:
        print('API.create(%s)' % meta)
        meta_hash = ''
    with open(upload_file, 'rb') as bfile:
        filebase = base64.b64encode(bfile.read()).decode('ascii')
        filename = os.path.basename(upload_file)
        if not GLOBAL.dry:
            API.upload(response['item']['meta']['meta_hash'], mimetype, filename, filebase)
        else:
            print('API.upload(__meta_hash__, %s, %s, __base64__ [%sB])' % (mimetype, filename, len(filebase)))
    return meta_hash

def clipboard(config, override_meta):
    print("clipboard")
    cmd, cmd_output, meta = get_config_for_option(config, override_meta, 'clipboard')
    print(cmd)
    print(subprocess.check_output(cmd, shell=True))
    with open(cmd_output, 'r') as clip:
        meta['text'] = clip.read()
    meta.update({'meta_type': 'clipboard'})
    if not GLOBAL.dry:
        response = API.create(meta)
        meta_hash = response['item']['meta']['meta_hash']
    else:
        print('API.create(%s)' % meta)
        meta_hash = ''
    #magic_mimetyper = Magic()
    #mimetype = magic_mimetyper.from_file(cmd_output)
    #with open(cmd_output, 'rb') as file:
    #    filebase = base64.b64encode(file.read()).decode('ascii')
    #    API.upload(response['item']['meta']['meta_hash'], mimetype, 'clipboard.txt', filebase)
    return meta_hash

def text(config, override_meta, text):
    print("text")
    common_meta = dict(config['default'])
    bashed_meta = {k:subprocess.getoutput('echo \'echo "%s"\' | bash' % v) for k,v in common_meta.items()}
    bashed_meta.update(override_meta)
    meta = bashed_meta
    meta['text'] = text
    meta.update({'meta_type': 'clipboard'})
    if not GLOBAL.dry:
        response = API.create(meta)
        meta_hash = response['item']['meta']['meta_hash']
    else:
        print('API.create(%s)' % meta)
        meta_hash = ''
    return meta_hash

def do_input(config, override_meta):
    print("input")
    cmd, cmd_output, meta = get_config_for_option(config, override_meta, 'input')
    print(cmd)
    print(subprocess.check_output(cmd, shell=True))
    with open(cmd_output, 'r') as inp:
        meta['text'] = inp.read()
    meta.update({'meta_type': 'note'})
    if not GLOBAL.dry:
        response = API.create(meta)
        meta_hash = response['item']['meta']['meta_hash']
    else:
        print('API.create(%s)' % meta)
        meta_hash = ''
    return meta_hash

if __name__ == '__main__':
    qs()
