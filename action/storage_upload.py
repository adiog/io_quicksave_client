# -*- coding: utf-8 -*-

"""
This file is a part of quicksave project.
Copyright (c) 2016 Aleksander Gajewski <adiog@brainfuck.pl>,
                   Adam Morawski <poczta@adammorawski.pl>.
"""

import requests

import environment


def storage_upload(files_data):
    response = requests.post(environment.get_url() +
                             '/api_bom/basic_http/storage/upload/',
                             files=files_data)
    response_json = response.json()
    print(response_json)
    assert(response_json['status'] == 'success')
    return response_json
