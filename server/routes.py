from flask import render_template, redirect, url_for, session, jsonify, request
from app import app, oauth, db
from models import User
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    redirect_uri = url_for('auth_callback', _external=True)
    logger.info(f'Redirect URI for login: {redirect_uri}')
    return oauth.google.authorize_redirect(redirect_uri)

@app.route('/auth/callback')
def auth_callback():
    try:
        token = oauth.google.authorize_access_token()
        logger.info(f'Token received: {token}')
        user_info = oauth.google.parse_id_token(token)
        logger.info(f'User info received: {user_info}')

        # Check if user already exists, if not create a new user
        user = User.query.filter_by(email=user_info['email']).first()
        if not user:
            user = User(username=user_info['name'], email=user_info['email'], verified=True)
            db.session.add(user)
            db.session.commit()

        session['user'] = user_info
        return redirect('/chat')
    except Exception as e:
        logger.error(f"Error during auth callback: {e}")
        return jsonify({'error': 'Authentication failed'}), 500

@app.route('/chat')
def chat():
    if 'user' not in session:
        return redirect('/')
    return render_template('chat.html', user=session['user'])
