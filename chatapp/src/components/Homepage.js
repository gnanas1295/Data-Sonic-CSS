import React, { useState, useEffect } from 'react';
import { googleSignIn, googleSignOut } from '../utils/googleAuth';
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
    const [recipientEmail, setRecipientEmail] = useState('');
    const [encryptedMessage, setEncryptedMessage] = useState('');

    useEffect(() => {
        const auth = getAuth();
        onAuthStateChanged(auth, (user) => {
            if (user) {
                setUser(user);
            } else {
                setUser(null);
            }
        });
    }, []);

    const handleLogin = async () => {
        try {
            const { user } = await googleSignIn();
            setUser(user);
        } catch (error) {
            console.error('Error logging in:', error);
        }
    };

    const handleLogout = async () => {
        try {
            await googleSignOut();
            setUser(null);
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

    const handleSendEmail = () => {
        if (!user) {
            setMessageStatus('Please log in first.');
            return;
        }

        const { publicKey: senderPublicKey, privateKey: senderPrivateKey } = generateKeyPair();
        setPublicKey(senderPublicKey);
        setPrivateKey(senderPrivateKey);

        const secretKey = "b'fY\x1aL\x0f\xe8V6\xb4\xbb\xc0\xb7\xd9\xe5\xa0\x1d]\x8b\x84\x8f\x14\xf3\xea\xd1'"; // Replace with your actual secret key
        const encryptedSecretKey = encryptWithPublicKey(secretKey, senderPublicKey);

        const subject = 'Your Encrypted Key';
        const body = `Here is the encrypted secret key:\n\n${encryptedSecretKey}\n\nVisit the following link to access the chat:\nhttp://localhost:3000/`;

        const mailtoLink = `mailto:${email}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
        window.location.href = mailtoLink;

        setMessageStatus('Email client opened.');
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
                            senderEmail={user.email}
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
