#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This file is a part of quicksave project.
Copyright (c) 2016 Aleksander Gajewski <adiog@brainfuck.pl>,
                   Adam Morawski <poczta@adammorawski.pl>.
"""

import json
import subprocess
import tempfile

from client_cli.action.item_create import item_create
from client_cli.action.storage_register import storage_register
from client_cli.action.storage_upload import storage_upload


def notify(title, message):
    subprocess.call(['notify-send', title, message])


def main():
    screenshot = tempfile.mktemp()
    subprocess.check_output(['gnome-screenshot', '--file', screenshot])

    file_path = screenshot
    content_type = 'application/png'

    request_data = json.dumps({'freetext': file_path})
    response_json = item_create(request_data)

    item_id = response_json['tid']

    files_data = {'file': (file_path, open(file_path, 'rb'), content_type)}
    response_json = storage_upload(files_data)
    file_path = response_json['file_hash']

    response_json = storage_register(item_id, content_type, file_path)
    print(response_json)
    notify('qs', 'screenshot has been saved')


if __name__ == '__main__':
    main()

