#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This file is a part of quicksave project.
Copyright (c) 2016 Aleksander Gajewski <adiog@brainfuck.pl>,
                   Adam Morawski <poczta@adammorawski.pl>.
"""

import json
import subprocess

from client_cli.action.item_create import item_create


def main():
    freetext = subprocess.check_output(['xsel', '--clipboard']).decode('utf-8')
    request_data = json.dumps({'freetext': freetext})
    response_json = item_create(request_data)
    print(response_json)


if __name__ == '__main__':
    main()
