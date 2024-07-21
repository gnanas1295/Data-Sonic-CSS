// components/Homepage.js

import React, { useState, useEffect } from 'react';
import { googleSignIn, googleSignOut, sendEmail } from '../utils/googleAuth';
import { generateKeyPair, encryptWithPublicKey, decryptWithPrivateKey } from '../utils/cryptoUtils';
import Chat from './Chat';
import './Homepage.css';
import { getAuth, onAuthStateChanged } from 'firebase/auth';

const Homepage = () => {
    const [email, setEmail] = useState('');
    const [publicKey, setPublicKey] = useState('');
    const [privateKey, setPrivateKey] = useState('');
    const [messageStatus, setMessageStatus] = useState('');
    const [user, setUser] = useState(null);
    const [token, setToken] = useState('');
    const [recipientEmail, setRecipientEmail] = useState('');
    const [encryptedMessage, setEncryptedMessage] = useState('');

    useEffect(() => {
        const auth = getAuth();
        onAuthStateChanged(auth, async (user) => {
            if (user) {
                setUser(user);
                const token = await user.getIdToken(true);
                setToken(token);
                console.log('Token:', token);
            } else {
                setUser(null);
                setToken('');
            }
        });
    }, []);

    const handleLogin = async () => {
        try {
            const { user, token } = await googleSignIn();
            setUser(user);
            setToken(token);
        } catch (error) {
            console.error('Error logging in:', error);
        }
    };

    const handleLogout = async () => {
        try {
            await googleSignOut();
            setUser(null);
            setToken('');
            setEmail('');
            setPublicKey('');
            setPrivateKey('');
            setMessageStatus('');
            setRecipientEmail('');
            setEncryptedMessage('');
        } catch (error) {
            console.error('Error logging out:', error);
        }
    };

    const handleSendEmail = async () => {
        if (!user || !token) {
            setMessageStatus('Please log in first.');
            return;
        }

        const { publicKey: senderPublicKey, privateKey: senderPrivateKey } = generateKeyPair();
        setPublicKey(senderPublicKey);
        setPrivateKey(senderPrivateKey);

        const secretKey = 'your-secret-key';
        const encryptedSecretKey = encryptWithPublicKey(secretKey, senderPublicKey);

        const subject = 'Your Encrypted Key';
        const body = `Here is the encrypted secret key:\n\n${encryptedSecretKey}\n\nVisit the following link to access the chat:\n[Your React App Link]`;

        try {
            await sendEmail(email, subject, body, token);
            setMessageStatus('Email sent successfully.');
        } catch (error) {
            console.error('Error sending email:', error);
            setMessageStatus('Error sending email.');
        }
    };

    const handleReceiveMessage = (encryptedMessage) => {
        if (!privateKey) {
            setMessageStatus('No private key available for decryption.');
            return;
        }
        try {
            const decryptedMessage = decryptWithPrivateKey(encryptedMessage, privateKey);
            setEncryptedMessage(decryptedMessage);
        } catch (error) {
            console.error('Error decrypting message:', error);
            setMessageStatus('Error decrypting message.');
        }
    };

    return (
        <div>
            {!user ? (
                <div>
                    <p>Please log in to continue.</p>
                    <button onClick={handleLogin}>Login with Google</button>
                </div>
            ) : (
                <div>
                    <div>
                        <button onClick={handleLogout}>Logout</button>
                    </div>
                    <div>
                        <h2>Send Email</h2>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="Recipient Email"
                        />
                        <button onClick={handleSendEmail}>Send Email</button>
                        {messageStatus && <p>{messageStatus}</p>}
                    </div>
                    <div>
                        <h2>Chat</h2>
                        <input
                            type="text"
                            value={recipientEmail}
                            onChange={(e) => setRecipientEmail(e.target.value)}
                            placeholder="Recipient Email"
                        />
                        <Chat
                            recipientEmail={recipientEmail}
                            onReceiveMessage={handleReceiveMessage}
                        />
                        {encryptedMessage && <p>Decrypted Message: {encryptedMessage}</p>}
                    </div>
                </div>
            )}
        </div>
    );
};

export default Homepage;
