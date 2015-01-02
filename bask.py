# imports
import sqlite3
from flask import Flask, render_template, request, session, g, redirect, url_for, \
    abort, render_template, flash
from contextlib import closing
from datetime import datetime

# configuration
DATABASE = 'D:/Documents/Bask/bask.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)

# DATABASE OPERATIONS

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


# ROUTES

@app.route('/')
def hello_world():
    cursor = g.db.execute('select * from event')
    events = [dict(event_id=row[0], description=row[1],
                   # parse date from sqlite 'date' (actually a string), then convert to readable format
                   event_date=datetime.strptime(row[2], '%Y-%m-%d').strftime('%A %b %d'),
                   # see docs on strftime in python and sqlite3 for formatting
                   event_time=datetime.strptime(row[3], '%H:%M').strftime('%I:%M %p'),
                   minors=row[5], cover=row[6], lat=row[7], lng=row[8])
              for row in cursor.fetchall()]
    return render_template('home.html', events=events)


@app.route('/about')
def about():
    return render_template('layout.html')


@app.route('/contact')
def contact():
    return render_template('layout.html')


# login
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('Welcome back', app.config['USERNAME'])
            return redirect(url_for('band'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('band'))


# Band event

@app.route('/band')
def band():
    cursor = g.db.execute('select * from event order by event_date desc')
    events = [dict(event_id=row[0], description=row[1],
                   # parse date from sqlite 'date' (actually a string), then convert to readable format
                   event_date=datetime.strptime(row[2], '%Y-%m-%d').strftime('%A %b %d'),
                   # see docs on strftime in python and sqlite3 for formatting
                   event_time=datetime.strptime(row[3], '%H:%M').strftime('%I:%M %p'),
                   minors=row[5], cover=row[6], lat=row[7], lng=row[8])
              for row in cursor.fetchall()]
    return render_template('band.html', events=events)


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into event (description, event_date, event_time, minors, cover, lat, lng) '
                 'values (?, ?, ?, ?, ?, ?, ?)',
                 [request.form['description'], request.form['event_date'], request.form['event_time'],
                  request.form['minors'], request.form['cover'], request.form['lat'], request.form['lng']])
    g.db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('band'))

# MAIN

if __name__ == '__main__':
    app.debug = True
    app.run()

