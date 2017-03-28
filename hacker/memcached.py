import json

import memcache

import env


token = get_token(uid)
session = {'token': token,
           'user': {}}

def register_session(session):
    client = memcache.Client([env.IO_QUICKSAVE_MEMCACHED_HOST, env.IO_QUICKSAVE_MEMCACHED_PORT)])
    client.set(token, json.dumps(session), time=300)