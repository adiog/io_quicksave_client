import sqlite3 as lite
db = env.IO_QUICKSAVE_DB_MASTER

def delete_users(l):
    with lite.connect(db) as con:
        for u in l:
            delete_from_user(con, u)

def delete_from_user(con, uid):
    cur = con.cursor()
    cur.execute('DELETE FROM user WHERE username LIKE "u%s"' % uid)

def create_user(uid):
    with lite.connect(db) as con:
        cur = con.cursor()
        username = 'u' + str(uid)
        password = 'p' + str(uid)
        cur.execute('INSERT INTO user (user_id, username, password, databaseConnectionString, filesystemConnectionString) VALUES(NULL, "%s", "%s", "%s", "%s")'
                    % (username, password, databaseConnectionString, filesystemConnectionString + str(uid)))