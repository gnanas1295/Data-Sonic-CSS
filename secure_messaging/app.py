from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import base64
import os
import logging

app = Flask(__name__, static_url_path='', static_folder='static')
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

# Generate DH parameters
parameters = dh.generate_parameters(generator=2, key_size=2048, backend=default_backend())

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

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
            recipient_public_key_pem = recipient.public_key.encode('utf-8')
            recipient_public_key = serialization.load_pem_public_key(recipient_public_key_pem, backend=default_backend())

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
        # Encrypt the message (simulated here, you should use proper encryption)
        encrypted_message = f"Encrypted message from {email}: {message}"

        # Send the encrypted message via email
        msg = Message('New Encrypted Message', sender=app.config['MAIL_USERNAME'], recipients=[recipient_email])
        msg.body = encrypted_message
        mail.send(msg)

        return jsonify({'message': 'Message sent!'}), 200
    else:
        return jsonify({'message': 'User not found!'}), 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
