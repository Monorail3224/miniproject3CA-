# INF601 - Advanced Programming in Python
# Clayton Allen
# Mini Project 3

import sqlite3
from db import init_db, query_db, close_connection, get_db
from flask import Flask, request, render_template, redirect, url_for, session, g
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your-secret-key'
DATABASE = 'tasks.db'


@app.teardown_appcontext
def teardown_db(exception):
    close_connection(exception)

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

        # Query the username using the user_id
        user = query_db('SELECT username FROM users WHERE id = ?', [user_id], one=True)
        if user:
            username = user[0]  # Accessing the first element of the tuple
        else:
            username = 'Unknown'  # or handle this case as you see fit

        return render_template('index.html', tasks=tasks, username=username)

@app.route('/add_task', methods=['GET', 'POST'])
def add_task():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        user_id = session['user_id']

        # Insert the new task into the database
        query_db('INSERT INTO tasks (title, description, user_id) VALUES (?, ?, ?)',
                 [title, description, user_id], commit=True)

        return redirect(url_for('index'))

    # For GET request, show the add task form
    return render_template('add_task.html')

@app.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Handle the task editing logic here
        title = request.form['title']
        description = request.form['description']

        # Update the task in the database based on task_id
        user_id = session['user_id']
        query_db('UPDATE tasks SET title=?, description=? WHERE id=? AND user_id=?',
                 [title, description, task_id, user_id], commit=True)

        return redirect(url_for('index'))

    # Fetch the task details from the database based on task_id
    user_id = session['user_id']
    task = query_db('SELECT * FROM tasks WHERE id=? AND user_id=?', [task_id, user_id], one=True)

    if task:
        # Pass the task details to the edit_task.html template
        return render_template('edit_task.html', task=task)

    # Handle the case where the task does not exist or doesn't belong to the user
    return "Task not found or unauthorized"

@app.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    user_id = session['user_id']

    # Check if the task with task_id exists and belongs to the user
    task = query_db('SELECT * FROM tasks WHERE id=? AND user_id=?', [task_id, user_id], one=True)

    if task:
        # Delete the task from the database
        query_db('DELETE FROM tasks WHERE id=?', [task_id], commit=True)
        return redirect(url_for('index'))

    # Handle the case where the task does not exist or doesn't belong to the user
    return "Task not found or unauthorized"




@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Check if username already exists
        existing_user = query_db('SELECT * FROM users WHERE username = ?', [username], one=True)
        if existing_user:
            return 'Username already exists!'

        # Insert the new user into the database
        query_db('INSERT INTO users (username, password) VALUES (?, ?)', [username, hashed_password], commit=True)
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # POST request logic
        username = request.form['username']
        password = request.form['password']
        user = query_db('SELECT * FROM users WHERE username = ?', [username], one=True)
        if user and check_password_hash(user[2], password):
            session['logged_in'] = True
            session['user_id'] = user[0]
            return redirect(url_for('index'))
        else:
            return 'Invalid username or password'
    else:
        # GET request logic
        return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

with app.app_context():
    init_db()
