import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

# Authentication Blueprint
bp = Blueprint('auth', __name__, url_prefix='/auth')


# Authentication Blueprint Methods

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        # Validate that username and password are not empty
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        # Validate that username is not already registered
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)   # qmark style
        ).fetchone() is not None:   
            error = 'User {} is already registered.'.format(username)
        
        if error is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()
            return redirect(url_for('auth.login'))
        
        flash(error)    # Error is not None

    # GET method
    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        # Try to retrieve user info from database
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        # Validate username and password
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'
        
        if error is None:
            session.clear()     # More info about session in Readme
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    # GET method
    return render_template('auth/login.html')

@bp.before_app_request # Register a function that runs before the view function
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Define a decorator to ensure the user is logged in
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view