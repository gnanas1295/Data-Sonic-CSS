from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

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

# Create the database
with app.app_context():
    db.create_all()

@app.route('/get-messages', methods=['GET'])
def get_messages():
    recipient = request.args.get('recipient')
    sender = request.args.get('sender')
    if not recipient or not sender:
        return jsonify({'error': 'Recipient and sender emails are required'}), 400

    # Fetch messages where either party is the sender or recipient
    messages = Message.query.filter(
        (Message.sender == sender and Message.recipient == recipient) |
        (Message.sender == recipient and Message.recipient == sender)
    ).all()

    messages_list = [{'sender': msg.sender, 'message': msg.encrypted_message} for msg in messages]
    return jsonify({'messages': messages_list}), 200

if __name__ == '__main__':
    app.run(debug=True)
