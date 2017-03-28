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

from quicksave_api import API, CDN


def main(url):
    response = CDN.get(url)
    print(response)
    print(response.headers['Content-Type'])
    print(response.text)


if __name__ == '__main__':
    main(sys.argv[1])
