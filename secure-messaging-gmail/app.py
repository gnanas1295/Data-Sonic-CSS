import logging
import os
import requests
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.backends import default_backend
from google.oauth2 import id_token
from google.auth.transport import requests as google_auth_requests

app = Flask(__name__, static_url_path='', static_folder='static')

# Set a secret key for the session management from environment variable
app.secret_key = os.getenv('SECRET_KEY')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'mruduladidde@gmail.com'
app.config['MAIL_PASSWORD'] = 'ubwo ayno qgql gaig'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

# Google OAuth settings from environment variables
app.config['GOOGLE_CLIENT_ID'] = os.getenv('GOOGLE_CLIENT_ID')
app.config['GOOGLE_CLIENT_SECRET'] = os.getenv('GOOGLE_CLIENT_SECRET')
app.config['GOOGLE_DISCOVERY_URL'] = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

# Generate DH parameters
parameters = dh.generate_parameters(generator=2, key_size=2048, backend=default_backend())

# OAuth2 client setup
def get_google_provider_cfg():
    return requests.get(app.config['GOOGLE_DISCOVERY_URL']).json()

@app.route('/')
def serve_index():
    return render_template('index.html')

@app.route('/login')
def login():
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    redirect_uri = url_for('google_auth_callback', _external=True)
    return redirect(authorization_endpoint + "?scope=openid%20email%20profile&response_type=code&client_id=" +
                    app.config['GOOGLE_CLIENT_ID'] + "&redirect_uri=" + redirect_uri)

@app.route('/google/callback')
def google_auth_callback():
    code = request.args.get('code')
    error = request.args.get('error')

    if error:
        return jsonify({'error': error}), 400

    if not code:
        return jsonify({'error': 'Authorization code not received'}), 400

    try:
        token_endpoint = get_google_provider_cfg()["token_endpoint"]
        redirect_uri = url_for('google_auth_callback', _external=True)

        token_url = token_endpoint
        params = {
            'code': code,
            'client_id': app.config['GOOGLE_CLIENT_ID'],
            'client_secret': app.config['GOOGLE_CLIENT_SECRET'],
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }

        token_response = requests.post(token_url, data=params)
        token_response.raise_for_status()

        id_token_value = token_response.json().get('id_token')

        # Verify the ID token
        id_info = id_token.verify_oauth2_token(
            id_token_value,
            google_auth_requests.Request(),
            app.config['GOOGLE_CLIENT_ID']
        )

        # Store the user's email in session or database as needed
        session['google_user'] = id_info['email']

        return redirect('/')  # Redirect to the home page or any other route after successful authentication
    except Exception as e:
        logging.error(f"Error in Google OAuth callback: {e}")
        return jsonify({'error': 'Failed to process Google OAuth callback'}), 500

@app.route('/logout')
def logout():
    session.pop('google_user', None)
    return redirect('/')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
