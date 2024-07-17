from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from google.oauth2 import id_token
from google.auth.transport import requests as google_auth_requests
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
import base64
import logging
import os
import requests

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

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    public_key = db.Column(db.Text, nullable=False)

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

    # Send public key to the user's email for verification
    msg = Message('Public Key Verification', sender=app.config['MAIL_USERNAME'], recipients=[email])
    msg.body = f"Your public key: {pem.decode('utf-8')}"
    mail.send(msg)

    return jsonify({'message': 'User registered successfully!'}), 201

@app.route('/exchange', methods=['POST'])
def exchange_keys():
    data = request.get_json()
    email = data['email']
    recipient_email = data['recipient_email']
    user = User.query.filter_by(email=email).first()
    recipient = User.query.filter_by(email=recipient_email).first()

    if user and recipient:
        try:
            logging.debug(f"User {email} and Recipient {recipient_email} found in database")

            recipient_public_key_pem = recipient.public_key.encode('utf-8')
            recipient_public_key = serialization.load_pem_public_key(recipient_public_key_pem, backend=default_backend())
            logging.debug(f"Recipient public key loaded: {recipient_public_key}")

            private_key = parameters.generate_private_key()
            logging.debug(f"Generated private key for {email}")

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

            return jsonify({'key': base64.urlsafe_b64encode(derived_key).decode('utf-8')}), 200
        except Exception as e:
            logging.error(f"Error during key exchange: {e}")
            return jsonify({'message': 'Key exchange failed!'}), 500
    else:
        logging.error(f"User {email} or recipient {recipient_email} not found in database")
        return jsonify({'message': 'User not found!'}), 404


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
            # Perform key exchange to get the shared key
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

            # Send the encrypted message via email
            msg = Message('New Encrypted Message', sender=app.config['MAIL_USERNAME'], recipients=[recipient_email])
            msg.body = f"IV: {iv_b64}\nEncrypted message: {encrypted_message_b64}"
            mail.send(msg)
            logging.debug(f"Encrypted message sent to {recipient_email}")

            return jsonify({'message': 'Message sent!'}), 200
        except Exception as e:
            logging.error(f"Error during message sending: {e}")
            return jsonify({'message': 'Message sending failed!'}), 500
    else:
        logging.error(f"User {email} or recipient {recipient_email} not found in database")
        return jsonify({'message': 'User not found!'}), 404


@app.route('/logout')
def logout():
    session.pop('google_user', None)
    return redirect('/')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
