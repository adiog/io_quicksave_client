# -*- coding: utf-8 -*-

"""
This file is a part of quicksave project.
Copyright (c) 2016 Aleksander Gajewski <adiog@brainfuck.pl>,
                   Adam Morawski <poczta@adammorawski.pl>.
"""

import environment
import requests

SESSION_COOKIE_NAME = 'sessionid'


def basic_login(username: str, password: str) -> str:
    url = environment.get_url() + '/api_auth/basic_login/'
    response = requests.get(url, auth=(username, password))
    response_json = response.json()
    assert response_json['status'] == 'success'
    assert response.cookies.get(SESSION_COOKIE_NAME) is not None
    session_id = response.cookies.get(SESSION_COOKIE_NAME)
    assert session_id is not None
    return session_id
