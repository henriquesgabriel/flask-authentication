import io
from flask import Blueprint, render_template, request, url_for, redirect, flash, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
import pyqrcode
from .data import User
from . import db

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    auth_code = request.form.get('auth_code')

    """
    Prevent users from accidentally being logged out when
    they close the browser
    """
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    if not user and not check_password_hash(user.password, password) or not user.verify_totp(auth_code):
        flash('Your email address, password or one-time password is incorrect.')
        return redirect(url_for('auth.login'))

    """
    Authorize and log the user in
    """
    login_user(user, remember=remember)

    return redirect(url_for('main.dashboard'))

@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    password = request.form.get('password')

    """
    Check if email exists in the database
    """
    user_email = User.query.filter_by(email=email).first()

    if user_email:
        flash('This email address already exists!')
        return redirect(url_for('auth.signup'))

    new_user = User(email=email, first_name=first_name, last_name=last_name, password=generate_password_hash(password, method='sha256'))

    db.session.add(new_user)
    db.session.commit()

    session['username'] = request.form.get('email')
    return redirect(url_for('auth.two_factor_setup'))

"""
2nd Factor Authentication Setup
"""
@auth.route('/two-factor-authentication')
def two_factor_setup():
    if 'username' not in session:
        return redirect(url_for('main.index'))
    user = User.query.filter_by(email=session['username']).first()
    if user is None:
        return redirect(url_for('main.index'))

    """
    Disable cache on client and server
    """
    return render_template('two-factor-setup.html'), 200, {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'}

"""
QR Code Generator
"""
@auth.route('/qrcode')
def qrcode():

    """
    Verify session
    """
    if 'username' not in session:
        abort(404)

    user = User.query.filter_by(email=session['username']).first()

    if user is None:
        abort(404)

    """
    Delete username from session
    """
    del session['username']

    """
    Render the QRCode for FreeTOTP token
    """
    url = pyqrcode.create(user.get_totp_uri())
    stream = io.BytesIO()
    url.svg(stream, scale=3)

    """
    Indicate the media type to return and disable cache
    """
    return stream.getvalue(), 200, {
        'Content-Type': 'image/svg+xml',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'}

"""
Ensure user is authenticated
"""
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
