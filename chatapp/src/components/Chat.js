import React, { useState } from 'react';
import axios from 'axios';
import { decryptWithSymmetricKey, encryptWithSymmetricKey } from '../utils/cryptoUtils';

const Chat = ({ privateKey, symmetricKey }) => {
    const [message, setMessage] = useState('');
    const [messages, setMessages] = useState([]);

    const handleSendMessage = async () => {
        const encryptedMessage = encryptWithSymmetricKey(message, symmetricKey);
        await axios.post('http://localhost:5000/send-message', { message: encryptedMessage });
        setMessages([...messages, { message: encryptedMessage, sender: 'Me' }]);
        setMessage('');
    };

    const fetchMessages = async () => {
        const response = await axios.get('http://localhost:5000/get-messages');
        const decryptedMessages = response.data.messages.map(msg => ({
            ...msg,
            message: decryptWithSymmetricKey(msg.message, symmetricKey),
        }));
        setMessages(decryptedMessages);
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
