import os
import sqlite3

from flask import Flask, request, session, g, \
        redirect, url_for, abort, render_template, \
        flash

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(
    dict(
        DATABASE=os.path.join(app.root_path, 'flaskr.db'),
        DEBUG=True,
        SECRET_KEY='\xe12\xc5\xff\x8c\xd2\x11\x12(\xe1\xc8\x03\x02Hl\xe4\x00\xe8(\x9f\xd106\x1c',
        USERNAME='admin',
        PASSWORD='admin'
    )
)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
    """
    Connect to a database
    """
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def get_db():
    """
    Opens a new DB connection if there's none in current app context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """
    Closes the DB connection.
    """
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute('select title, text from entries order by id desc')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into entries(title, text) values (?, ?)', [request.form['title'], request.form['text']])
    db.commit()
    flash('New Entry added successfully!')
    return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid User!'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid Password!'
        else:
            session['logged_in'] = True
            flash('You\'re now logged in!')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You\'re now logged out!')
    return redirect(url_for('show_entries'))

if __name__ == '__main__':
    app.run()
