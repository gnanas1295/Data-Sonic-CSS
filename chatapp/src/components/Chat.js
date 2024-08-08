import React, { useState } from 'react';
import './ChatPage.css';
import { encryptWithSymmetricKey } from '../utils/cryptoUtils';

const Chat = ({ recipientEmail, onReceiveMessage, symmetricKey }) => {
    const [message, setMessage] = useState('');
    const [messageStatus, setMessageStatus] = useState('');

    const handleSendMessage = async () => {
        // if (!symmetricKey) {
        //     setMessageStatus('No symmetric key available for encryption.');
        //     return;
        // }
        try {
            const encryptedMessage = encryptWithSymmetricKey(message, symmetricKey);
            // Send the encrypted message up to the parent component
            onReceiveMessage(encryptedMessage);
            setMessage('');
            setMessageStatus('Message sent successfully.');
        } catch (error) {
            console.error('Error encrypting message:', error);
            setMessageStatus('Error encrypting message.');
        }
    };

    return (
        <div className="chat-page">
            <h2>Chat with {recipientEmail}</h2>
            <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Enter your message"
            />
            <button onClick={handleSendMessage}>Send Message</button>
            {messageStatus && <p>{messageStatus}</p>}
        </div>
    );
};

export default Chat;
