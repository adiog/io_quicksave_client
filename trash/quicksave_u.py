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
from magic import Magic
import magic.flags

from quicksave_api import API


def upload(filepath, target_filename=None, metatype=None):
    magic_mimetyper = Magic()
    mimetype = magic_mimetyper.from_file(filepath)
    if not metatype:
        metatype = mimetype
    #print(mimetype)
    if not target_filename:
        target_filename = os.path.basename(filepath)

    createRespenseBean = API.create(metatype, target_filename, '', '', '')

    with open(filepath, 'rb') as file:
        filebase = base64.b64encode(file.read()).decode('ascii')
        #print(filebase)
        #print(len(filebase))
        response = API.upload(createRespenseBean['item']['meta']['meta_hash'], mimetype, target_filename, filebase)
        if response['message'] == 'OK':
            print('File uploaded successfully: https://cdn.quicksave.io/%s/%s/%s' % (createRespenseBean['item']['meta']['user_hash'], createRespenseBean['item']['meta']['meta_hash'], response['hash']))
    #request_data = json.dumps({'freetext': sys.argv[1]})
    #response_json = item_create(request_data)
    #print(response_json)



if __name__ == '__main__':
    upload(sys.argv[1])
