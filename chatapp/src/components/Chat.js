import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { decryptWithSymmetricKey, encryptWithSymmetricKey, generateSymmetricKey } from '../utils/cryptoUtils';

const Chat = ({ recipientEmail, onReceiveMessage, user }) => {
    const [message, setMessage] = useState('');
    const [messages, setMessages] = useState([]);
    const [symmetricKey, setSymmetricKey] = useState('');

    useEffect(() => {
        if (recipientEmail) {
            // Generate a symmetric key for the session
            const key = generateSymmetricKey();
            setSymmetricKey(key);
        }
    }, [recipientEmail]);

    const handleSendMessage = async () => {
        const encryptedMessage = encryptWithSymmetricKey(message, symmetricKey);
        await axios.post('http://127.0.0.1:5000/send-message', {
            recipient: recipientEmail,
            message: encryptedMessage,
            sender: user
        });
        setMessages([...messages, { message: encryptedMessage, sender: user }]);
        setMessage('');
    };

    const fetchMessages = async () => {
        const response = await axios.get('http://127.0.0.1:5000/get-messages', { params: { recipient: recipientEmail } });
        const decryptedMessages = response.data.messages.map(msg => ({
            ...msg,
            message: decryptWithSymmetricKey(msg.message, symmetricKey),
        }));
        setMessages(decryptedMessages);
        onReceiveMessage(decryptedMessages);
    };

    return (
        <div>
            <div>
                {messages.map((msg, index) => (
                    <div key={index}>{msg.sender}: {msg.message}</div>
                ))}
            </div>
            <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
            />
            <button onClick={handleSendMessage}>Send</button>
            <button onClick={fetchMessages}>Fetch Messages</button>
        </div>
    );
};

export default Chat;
