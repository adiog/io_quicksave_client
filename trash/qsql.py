#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This file is a part of quicksave project.
Copyright (c) 2016 Aleksander Gajewski <adiog@brainfuck.pl>,
                   Adam Morawski <poczta@adammorawski.pl>.
"""

import json
import sys
from client_cli.action.qsql_query import qsql_query


def main():
    request_data = json.dumps({'query': sys.argv[1]})
    response_json = qsql_query(request_data)
    print(response_json)


if __name__ == '__main__':
    main()
