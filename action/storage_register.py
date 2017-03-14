# -*- coding: utf-8 -*-

"""
This file is a part of quicksave project.
Copyright (c) 2016 Aleksander Gajewski <adiog@brainfuck.pl>,
                   Adam Morawski <poczta@adammorawski.pl>.
"""

import environment
import json
import requests


def storage_register(item_id, content_type, file_path):
    request_data = json.dumps({'item_id': item_id,
                               'content_type': content_type,
                               'storage': file_path})
    response = requests.post(environment.get_url() +
                             '/api_bom/basic_http/storage/register/',
                             data=request_data,
                             auth=(environment.get_test_user_username(),
                                   environment.get_test_user_password()))
    response_json = response.json()
    print(response_json)
    assert(response_json['status'] == 'success')
    return response_json
