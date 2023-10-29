import sqlite3
from db import init_db, query_db
from flask import Flask, request, render_template, redirect, url_for, session, g
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your-secret-key'
DATABASE = 'tasks.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False, commit=False):
    cur = get_db().execute(query, args)
    if commit:
        get_db().commit()
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        user_id = session.get('user_id')
        tasks = query_db('SELECT * FROM tasks WHERE user_id = ?', [user_id])
        return render_template('index.html', tasks=tasks)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = query_db('SELECT * FROM users WHERE username = ?', [username], one=True)
        if user and check_password_hash(user[2], password):
            session['logged_in'] = True
            session['user_id'] = user[0]
            return redirect(url_for('index'))
        else:
            return 'Invalid username or password'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/add_task', methods=['POST'])
def add_task():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    title = request.form['title']
    description = request.form['description']
    user_id = session.get('user_id')
    query_db('INSERT INTO tasks (title, description, user_id) VALUES (?, ?, ?)',
             [title, description, user_id], commit=True)
    return redirect(url_for('index'))

# Add more routes for editing and deleting tasks

if __name__ == '__main__':
    init_db(app)
    app.run(debug=True)
