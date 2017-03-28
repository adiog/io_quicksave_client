#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This file is a part of quicksave project.
Copyright (c) 2017 Aleksander Gajewski <adiog@quicksave.io>.
"""
import base64
import configparser
import os
import subprocess
import tempfile
from os.path import expanduser
import argparse

import re

from magic import Magic

from quicksave_api import API

meta_override_arguments = ['icon', 'name', 'text', 'author', 'source_url', 'source_title']


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
    parser.add_argument("-T", "--token-file", help="use token file [default ~/.quicksave.token]")

    parser.add_argument("-U", "--username", help="authenticate with username")
    parser.add_argument("-P", "--password", help="authenticate with password [unsafe!]")

    parser.add_argument("-q", "--query", help="retrieve items by QSQL query")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-s", "--screenshot", help="quicksave screenshot", action="store_true")
    group.add_argument("-a", "--area", help="quicksave screenshot with area picker", action="store_true")
    group.add_argument("-f", "--file", help="quicksave file")
    group.add_argument("-c", "--clipboard", help="quicksave current clipboard content", action="store_true")
    group.add_argument("-t", "--text", help="quciksave text")
    group.add_argument("-i", "--input", help="quicksave text with external editor", action="store_true")
    group.add_argument("-k", "--key", help="get authentication token [default]", action="store_true")

    setter_group = parser.add_argument_group()
    for meta_attr in meta_override_arguments:
        setter_group.add_argument("--set-" + meta_attr, metavar=meta_attr.upper(), help="override default " + meta_attr)

    args = parser.parse_args()

    home = expanduser("~")

    if args.config_file:
        config_file = args.config_file
    else:
        config_file = home + '/.quicksave.ini'

    if args.token_file:
        token_file = args.token_file
    else:
        token_file = home + '/.quicksave.token'

    config = configparser.ConfigParser()
    config.read(config_file)

    if args.username:
        username = args.username
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

    #subprocess.getoutput

    if args.screenshot:
        screenshot(config, override_meta)
    elif args.area:
        area(config, override_meta)
    elif args.file:
        file(config, override_meta, args.file)
    elif args.clipboard:
        clipboard(config, override_meta)
    elif args.text:
        text(config, override_meta, args.text)
    elif args.input:
        do_input(config, override_meta)
    else:
        print("just getting token")


def screenshot(config, override_meta):
    print("screenhot")
    cmd, cmd_output, meta = get_config_for_option(config, override_meta, 'screenshot')
    print(cmd)
    print(subprocess.check_output(cmd.split(' ')))
    meta.update({'meta_type': 'screenshot'})
    response = API.create(meta)
    magic_mimetyper = Magic()
    mimetype = magic_mimetyper.from_file(cmd_output)
    with open(cmd_output, 'rb') as file:
        filebase = base64.b64encode(file.read()).decode('ascii')
        API.upload(response['item']['meta']['meta_hash'], mimetype, 'screenshot.png', filebase)

def area(config, override_meta):
    print("area")
    cmd, cmd_output, meta = get_config_for_option(config, override_meta, 'area')
    print(cmd)
    print(subprocess.check_output(cmd.split(' ')))
    meta.update({'meta_type': 'screenshot'})
    response = API.create(meta)
    magic_mimetyper = Magic()
    mimetype = magic_mimetyper.from_file(cmd_output)
    with open(cmd_output, 'rb') as file:
        filebase = base64.b64encode(file.read()).decode('ascii')
        API.upload(response['item']['meta']['meta_hash'], mimetype, 'screenshot.png', filebase)

def file(config, override_meta, upload_file):
    print("file")

    common_meta = dict(config['default'])
    bashed_meta = {k:subprocess.getoutput('echo \'echo "%s"\' | bash' % v) for k,v in common_meta.items()}
    bashed_meta.update(override_meta)

    meta = bashed_meta
    meta.update({'meta_type': 'file'})
    response = API.create(meta)
    magic_mimetyper = Magic()
    mimetype = magic_mimetyper.from_file(upload_file)
    with open(upload_file, 'rb') as bfile:
        filebase = base64.b64encode(bfile.read()).decode('ascii')
        target_filename = os.path.basename(upload_file)
        API.upload(response['item']['meta']['meta_hash'], mimetype, target_filename, filebase)

def clipboard(config, override_meta):
    print("clipboard")
    cmd, cmd_output, meta = get_config_for_option(config, override_meta, 'clipboard')
    print(cmd)
    print(subprocess.check_output(cmd, shell=True))
    with open(cmd_output, 'r') as clip:
        meta['text'] = clip.read()
    meta.update({'meta_type': 'clipboard'})
    response = API.create(meta)
    #magic_mimetyper = Magic()
    #mimetype = magic_mimetyper.from_file(cmd_output)
    #with open(cmd_output, 'rb') as file:
    #    filebase = base64.b64encode(file.read()).decode('ascii')
    #    API.upload(response['item']['meta']['meta_hash'], mimetype, 'clipboard.txt', filebase)

def text(config, override_meta, text):
    print("text")
    common_meta = dict(config['default'])
    bashed_meta = {k:subprocess.getoutput('echo \'echo "%s"\' | bash' % v) for k,v in common_meta.items()}
    bashed_meta.update(override_meta)
    meta = bashed_meta
    meta['text'] = text
    meta.update({'meta_type': 'clipboard'})
    response = API.create(meta)

def do_input(config, override_meta):
    print("input")
    cmd, cmd_output, meta = get_config_for_option(config, override_meta, 'input')
    print(cmd)
    print(subprocess.check_output(cmd, shell=True))
    with open(cmd_output, 'r') as inp:
        meta['text'] = inp.read()
    meta.update({'meta_type': 'note'})
    response = API.create(meta)

if __name__ == '__main__':
    qs()
