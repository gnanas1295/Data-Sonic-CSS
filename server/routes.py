import traceback
from flask import render_template, redirect, url_for, session, jsonify, request
from app import app, oauth, db
from models import User
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
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

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data['email']
    username = data['username']
    password = data['password']

    try:
        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'message': 'Email already registered'}), 400

        verification_code = os.urandom(6).hex()
        new_user = User(username=username, email=email, password=password, verification_code=verification_code)
        db.session.add(new_user)
        db.session.commit()
        send_verification_email(email, verification_code)
        return jsonify({'message': 'Registration successful, please verify your email'}), 201

    except Exception as e:
        logger.error(f"An error occurred during registration: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'message': 'An internal error occurred'}), 500


@app.route('/verify_email', methods=['POST'])
def verify_email():
    data = request.json
    email = data['email']
    code = data['code']
    user = User.query.filter_by(email=email, verification_code=code).first()
    if user:
        user.verified = True
        db.session.commit()
        return jsonify({'message': 'Email verified successfully'}), 200
    return jsonify({'message': 'Invalid verification code'}), 400

def send_verification_email(email, code):
    # Email configuration
    sender_email = os.environ.get('SENDER_EMAIL')
    sender_password = os.environ.get('SENDER_PASSWORD')

    # Log email settings for debugging
    logger.info(f'Sender Email: {sender_email}')
    logger.info(f'Sender Password: {"***" if sender_password else None}')

    if not sender_email or not sender_password:
        logger.error('SENDER_EMAIL or SENDER_PASSWORD environment variable is not set')
        return

    smtp_server = 'smtp.gmail.com'
    smtp_port = 587  # For SSL use 465

    # Create message
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = email
    message['Subject'] = 'Verification Code for Resort Chatbot'

    body = f'Your verification code is: {code}. Enter this code to complete registration.'
    message.attach(MIMEText(body, 'plain'))

    # Connect to SMTP server and send email
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Secure the connection
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, message.as_string())
        logger.info("Email sent successfully!")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
    finally:
        server.quit()
