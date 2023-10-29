import sqlite3
from flask import g

DATABASE = 'tasks.db'

def init_db():
    db = get_db()
    cursor = db.cursor()

    # Check if the 'users' table exists and create if it doesn't
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
    if not cursor.fetchone():
        with open('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
    
    db.commit()


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


def query_db(query, args=(), one=False, commit=False):
    cur = get_db().execute(query, args)
    if commit:
        get_db().commit()
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def close_connection(exception=None):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
