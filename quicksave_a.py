#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This file is a part of quicksave project.
Copyright (c) 2017 Aleksander Gajewski <adiog@quicksave.io>.
"""
import base64
import datetime
import json
import os
import subprocess
import sys
import tempfile

from quicksave_api import API
from quicksave_u import upload


def main():
    filename = tempfile.NamedTemporaryFile().name
    subprocess.check_output(['gnome-screenshot', '-a', '-f', filename])
    upload(filename, 'Screenshot.png', 'screenshot')


if __name__ == '__main__':
    main()
