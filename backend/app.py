from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)

#Configuring the DB
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

# Store messages as a list of dictionaries
# messages = []

@app.route('/send-message', methods=['POST'])
def send_message():
    data = request.json
    recipient = data['recipient']
    message = data['message']
    sender = data.get('sender', 'Anonymous')  # Default sender if not provided
    new_message = Message(recipient=recipient, sender=sender, encrypted_message=message)
    # messages.append({'recipient': recipient, 'message': message, 'sender': sender})
    print("Messages: ", new_message)
    db.session.add(new_message)
    db.session.commit()
    return jsonify({'status': 'Message sent'}), 200

@app.route('/get-messages', methods=['GET'])
def get_messages():
    # recipient = request.args.get('recipient')
    # if not recipient:
    #     return jsonify({'error': 'Recipient email is required'}), 400

    # # recipient_messages = [msg for msg in messages if msg['recipient'] == recipient]
    # # return jsonify({'messages': recipient_messages}), 200
    # recipient_messages = Message.query.filter_by(recipient=recipient).all()
    # messages_list = [{'sender': msg.sender, 'message': msg.encrypted_message} for msg in recipient_messages]
    # return jsonify({'messages': messages_list}), 200
    sender = request.args.get('recipient')
    if not sender:
        return jsonify({'error': 'Sender email is required'}), 400

    # recipient_messages = [msg for msg in messages if msg['recipient'] == recipient]
    # return jsonify({'messages': recipient_messages}), 200
    sender_messages = Message.query.filter_by(sender=sender).all()
    messages_list = [{'sender': msg.sender, 'message': msg.encrypted_message} for msg in sender_messages]
    return jsonify({'messages': messages_list}), 200

if __name__ == '__main__':
    app.run(debug=True)
