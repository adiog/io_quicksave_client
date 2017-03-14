#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This file is a part of quicksave project.
Copyright (c) 2016 Aleksander Gajewski <adiog@brainfuck.pl>,
                   Adam Morawski <poczta@adammorawski.pl>.
"""

import json
import sys

from client_cli.action.tag_create import tag_create


def main():
    item_id = sys.argv[1]
    tag = sys.argv[2]
    request_json = {'item_id': item_id, 'tag': tag}
    if len(sys.argv) > 3:
        value = sys.argv[3]
        request_json.update({'value': value})
    request_data = json.dumps(request_json)
    response_json = tag_create(request_data)
    print(response_json)


if __name__ == '__main__':
    main()
