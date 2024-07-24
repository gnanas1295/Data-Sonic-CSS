from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configuring the DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///messages.db'
db = SQLAlchemy(app)

# Define the Message model
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipient = db.Column(db.String(120), nullable=False)
    sender = db.Column(db.String(120), nullable=False)
    encrypted_message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

# Create the database
with app.app_context():
    db.create_all()

@app.route('/send-message', methods=['POST'])
def send_message():
    data = request.json
    recipient = data['recipient']
    message = data['message']
    sender = data.get('sender', 'Anonymous')  # Default sender if not provided
    new_message = Message(recipient=recipient, sender=sender, encrypted_message=message)
    db.session.add(new_message)
    db.session.commit()
    return jsonify({'status': 'Message sent'}), 200

@app.route('/get-messages', methods=['GET'])
def get_messages():
    user_email = request.args.get('user')
    if not user_email:
        return jsonify({'error': 'User email is required'}), 400

    # Fetch messages where the user is either the sender or the recipient
    user_messages = Message.query.filter(
        (Message.sender == user_email) | (Message.recipient == user_email)
    ).order_by(Message.timestamp).all()

    messages_list = [{'sender': msg.sender, 'recipient': msg.recipient, 'message': msg.encrypted_message, 'timestamp': msg.timestamp} for msg in user_messages]
    return jsonify({'messages': messages_list}), 200

if __name__ == '__main__':
    app.run(debug=True)
