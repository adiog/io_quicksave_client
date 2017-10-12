# This file is a part of quicksave project.
# Copyright (c) 2017 Aleksander Gajewski <adiog@quicksave.io>.

import getpass


def cli_credentials_prompt():
    username = input('Username [%s]: ' % getpass.getuser())
    if username == '':
        username = getpass.getuser()
    password = getpass.getpass('Password: ')
    return username, password
