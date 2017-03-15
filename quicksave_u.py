#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This file is a part of quicksave project.
Copyright (c) 2017 Aleksander Gajewski <adiog@quicksave.io>.
"""
import base64
import json
import os
import sys

from quicksave_api import API


def main(filepath):
    filename = os.path.basename(filepath)
    with open(filename, 'rb') as file:
        filebase = base64.b64encode(file.read()).decode('ascii')
        print(filebase)
        print(len(filebase))
        API.upload(666, filename, filebase)
    #request_data = json.dumps({'freetext': sys.argv[1]})
    #response_json = item_create(request_data)
    #print(response_json)


if __name__ == '__main__':
    main(sys.argv[1])
