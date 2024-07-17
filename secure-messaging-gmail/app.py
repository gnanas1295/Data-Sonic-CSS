from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from google.oauth2 import id_token
from google.auth.transport import requests as google_auth_requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.exceptions import InvalidKey, InvalidSignature
import base64
import logging
import os
import requests
import json
from urllib.parse import urlencode

app = Flask(__name__, static_url_path='', static_folder='static')
app.secret_key = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    public_key = db.Column(db.Text, nullable=False)

app.config['GOOGLE_CLIENT_ID'] = os.getenv('GOOGLE_CLIENT_ID')
app.config['GOOGLE_CLIENT_SECRET'] = os.getenv('GOOGLE_CLIENT_SECRET')
app.config['GOOGLE_DISCOVERY_URL'] = "https://accounts.google.com/.well-known/openid-configuration"

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
    scopes = [
        "openid",
        "email",
        "profile",
        "https://www.googleapis.com/auth/gmail.send"
    ]
    params = {
        'scope': ' '.join(scopes),
        'response_type': 'code',
        'client_id': app.config['GOOGLE_CLIENT_ID'],
        'redirect_uri': redirect_uri,
        'access_type': 'offline',
        'prompt': 'consent'
    }
    return redirect(authorization_endpoint + "?" + urlencode(params))


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

        tokens = token_response.json()
        id_token_value = tokens.get('id_token')
        access_token = tokens.get('access_token')
        refresh_token = tokens.get('refresh_token')

        id_info = id_token.verify_oauth2_token(
            id_token_value,
            google_auth_requests.Request(),
            app.config['GOOGLE_CLIENT_ID']
        )

        session['google_user'] = id_info['email']
        session['tokens'] = tokens

        return redirect('/')
    except Exception as e:
        logging.error(f"Error in Google OAuth callback: {e}")
        return jsonify({'error': 'Failed to process Google OAuth callback'}), 500



@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data['email']
    private_key = parameters.generate_private_key()
    public_key = private_key.public_key()
    pem = public_key.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)
    user = User(email=email, public_key=pem.decode('utf-8'))
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully!'}), 201

@app.route('/exchange', methods=['POST'])
def exchange_keys():
    data = request.get_json()
    email = data.get('email')
    recipient_email = data.get('recipient_email')
    user = User.query.filter_by(email=email).first()
    recipient = User.query.filter_by(email=recipient_email).first()

    if not user or not recipient:
        return jsonify({'message': 'User or recipient not found!'}), 404

    try:
        logging.debug(f"User {email} and Recipient {recipient_email} found in database")

        recipient_public_key_pem = recipient.public_key.encode('utf-8')
        recipient_public_key = serialization.load_pem_public_key(recipient_public_key_pem, backend=default_backend())
        logging.debug(f"Recipient public key loaded: {recipient_public_key}")

        private_key = parameters.generate_private_key()
        logging.debug(f"Generated private key for {email}")

        shared_key = private_key.exchange(recipient_public_key)
        logging.debug(f"Shared key computed successfully between {email} and {recipient_email}")

        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'handshake data',
            backend=default_backend()
        ).derive(shared_key)

        return jsonify({'key': base64.urlsafe_b64encode(derived_key).decode('utf-8')}), 200
    except Exception as e:
        logging.error(f"Error during key exchange: {e}")
        return jsonify({'message': 'Key exchange failed!'}), 500

def get_gmail_service():
    tokens = session.get('tokens')
    if not tokens:
        raise Exception("No tokens available")

    creds = Credentials(
        token=tokens['access_token'],
        refresh_token=tokens.get('refresh_token'),
        token_uri=get_google_provider_cfg()["token_endpoint"],
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET']
    )

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        session['tokens']['access_token'] = creds.token
        session['tokens']['refresh_token'] = creds.refresh_token  # Ensure refresh_token is also updated

    service = build('gmail', 'v1', credentials=creds)
    return service


@app.route('/send', methods=['POST'])
def send_message():
    data = request.get_json()
    email = data['email']
    recipient_email = data['recipient_email']
    message = data['message']

    user = User.query.filter_by(email=email).first()
    recipient = User.query.filter_by(email=recipient_email).first()

    if user and recipient:
        try:
            logging.debug(f"Starting key exchange for user {email} and recipient {recipient_email}")

            recipient_public_key_pem = recipient.public_key.encode('utf-8')
            recipient_public_key = serialization.load_pem_public_key(recipient_public_key_pem, backend=default_backend())
            logging.debug(f"Recipient public key loaded: {recipient_public_key}")

            private_key = parameters.generate_private_key()
            shared_key = private_key.exchange(recipient_public_key)
            logging.debug(f"Shared key computed successfully between {email} and {recipient_email}")

            # Derive AES key from shared key
            derived_key = HKDF(
                algorithm=hashes.SHA256(),
                length=32,
                salt=None,
                info=b'handshake data',
                backend=default_backend()
            ).derive(shared_key)
            logging.debug(f"AES key derived successfully")

            # Encrypt the message using AES
            iv = os.urandom(16)
            cipher = Cipher(algorithms.AES(derived_key), modes.CBC(iv), backend=default_backend())
            encryptor = cipher.encryptor()

            # Pad the message to be AES block size compatible
            padder = padding.PKCS7(128).padder()
            padded_message = padder.update(message.encode()) + padder.finalize()

            encrypted_message = encryptor.update(padded_message) + encryptor.finalize()
            logging.debug(f"Message encrypted successfully")

            # Encode the IV and the encrypted message in a way that can be sent via email
            iv_b64 = base64.urlsafe_b64encode(iv).decode('utf-8')
            encrypted_message_b64 = base64.urlsafe_b64encode(encrypted_message).decode('utf-8')

            # Send the encrypted message via Gmail API
            service = get_gmail_service()
            email_message = f"To: {recipient_email}\r\nSubject: New Encrypted Message\r\n\r\nIV: {iv_b64}\nEncrypted message: {encrypted_message_b64}"
            encoded_message = base64.urlsafe_b64encode(email_message.encode('utf-8')).decode('utf-8')

            message = (service.users().messages().send(
                userId="me",
                body={'raw': encoded_message}
            ).execute())

            logging.debug(f"Encrypted message sent to {recipient_email}")

            return jsonify({'message': 'Message sent!'}), 200

        except InvalidKey as e:
            logging.error(f"Invalid recipient's public key: {e}")
            return jsonify({'message': 'Invalid recipient\'s public key'}), 500

        except InvalidSignature as e:
            logging.error(f"Invalid signature: {e}")
            return jsonify({'message': 'Invalid signature'}), 500

        except ValueError as e:
            logging.error(f"ValueError during key exchange or encryption: {e}")
            return jsonify({'message': 'Error during key exchange or encryption'}), 500

        except Exception as e:
            logging.error(f"Error during message sending: {e}")
            return jsonify({'message': 'Message sending failed!'}), 500

    else:
        logging.error(f"User {email} or recipient {recipient_email} not found in database")
        return jsonify({'message': 'User not found!'}), 404



@app.route('/logout')
def logout():
    session.pop('google_user', None)
    session.pop('tokens', None)
    return redirect('/')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
