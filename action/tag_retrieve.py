# -*- coding: utf-8 -*-

"""
This file is a part of quicksave project.
Copyright (c) 2016 Aleksander Gajewski <adiog@brainfuck.pl>,
                   Adam Morawski <poczta@adammorawski.pl>.
"""

import environment
import requests


def tag_retrieve(request_data):
    response = requests.get(environment.get_url() +
                            '/api_bom/basic_http/tag/retrieve/',
                            data=request_data,
                            auth=(environment.get_test_user_username(),
                                  environment.get_test_user_password()))
    response_json = response.json()
    print(response_json)
    assert(response_json['status'] == 'success')
    return response_json

