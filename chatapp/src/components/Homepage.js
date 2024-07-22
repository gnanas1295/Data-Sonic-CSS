import React, { useState, useEffect } from 'react';
import { googleSignIn, googleSignOut } from '../utils/googleAuth';
import { generateKeyPair, encryptWithPublicKey, decryptWithPrivateKey, generateSymmetricKey, decryptWithSymmetricKey } from '../utils/cryptoUtils';
import Chat from './Chat';
import './Homepage.css';
import { getAuth, onAuthStateChanged } from 'firebase/auth';
import axios from 'axios';

const Homepage = () => {
    const [email, setEmail] = useState('');
    const [publicKey, setPublicKey] = useState('');
    const [privateKey, setPrivateKey] = useState('');
    const [recipientPublicKey, setRecipientPublicKey] = useState('');
    const [messageStatus, setMessageStatus] = useState('');
    const [user, setUser] = useState(null);
    const [recipientEmail, setRecipientEmail] = useState('');
    const [encryptedMessage, setEncryptedMessage] = useState('');
    const [encryptedSymmetricKey, setEncryptedSymmetricKey] = useState('');
    const [symmetricKey, setSymmetricKey] = useState('');

    useEffect(() => {
        const auth = getAuth();
        onAuthStateChanged(auth, (user) => {
            if (user) {
                setUser(user);
                // Generate key pair when the user logs in
                const { publicKey: userPublicKey, privateKey: userPrivateKey } = generateKeyPair();
                setPublicKey(userPublicKey);
                setPrivateKey(userPrivateKey);
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
            setEncryptedSymmetricKey('');
            setSymmetricKey('');
            setRecipientPublicKey('');
        } catch (error) {
            console.error('Error logging out:', error);
        }
    };

    const handleSendPublicKey = () => {
        if (!user || !recipientEmail || !publicKey) {
            setMessageStatus('Please log in and provide recipient email.');
            return;
        }

        const subject = 'Your Public Key';
        const body = `Here is my public key:\n\n${publicKey}\n\nPlease use this public key to encrypt messages or symmetric keys for me.`;

        const mailtoLink = `mailto:${recipientEmail}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
        window.location.href = mailtoLink;

        setMessageStatus('Email client opened to send public key.');
    };

    const handleSendEncryptedSymmetricKey = () => {
        if (!user || !recipientPublicKey) {
            setMessageStatus('Please log in and provide recipient public key.');
            return;
        }

        const secretKey = generateSymmetricKey();
        const encryptedSecretKey = encryptWithPublicKey(secretKey, recipientPublicKey);

        const subject = 'Your Encrypted Symmetric Key';
        const body = `Here is the encrypted symmetric key:\n\n${encryptedSecretKey}\n\nVisit the following link to access the chat:\nhttp://localhost:3000/`;

        const mailtoLink = `mailto:${email}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
        window.location.href = mailtoLink;

        setMessageStatus('Email client opened to send encrypted symmetric key.');
    };

    const handleDecryptSymmetricKey = () => {
        if (!privateKey || !encryptedSymmetricKey) {
            setMessageStatus('Private key or encrypted symmetric key is missing.');
            return;
        }
        try {
            const decryptedKey = decryptWithPrivateKey(encryptedSymmetricKey, privateKey);
            setSymmetricKey(decryptedKey);
            setMessageStatus('Symmetric key decrypted successfully.');
        } catch (error) {
            console.error('Error decrypting symmetric key:', error);
            setMessageStatus('Error decrypting symmetric key.');
        }
    };

    const handleReceiveMessage = (encryptedMessage) => {
        if (!symmetricKey) {
            setMessageStatus('No symmetric key available for decryption.');
            return;
        }
        try {
            const decryptedMessage = decryptWithSymmetricKey(encryptedMessage, symmetricKey);
            setEncryptedMessage(decryptedMessage);
        } catch (error) {
            console.error('Error decrypting message:', error);
            setMessageStatus('Error decrypting message.');
        }
    };

    const handlePublicKeyChange = (e) => {
        setRecipientPublicKey(e.target.value);
    };

    return (
        <div className="chat-window">
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
                        <h2>Send Public Key</h2>
                        <input
                            type="email"
                            value={recipientEmail}
                            onChange={(e) => setRecipientEmail(e.target.value)}
                            placeholder="Recipient Email"
                        />
                        <button onClick={handleSendPublicKey}>Send Public Key</button>
                        {messageStatus && <p>{messageStatus}</p>}
                    </div>
                    <div>
                        <h2>Send Encrypted Symmetric Key</h2>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="Recipient Email"
                        />
                        <input
                            type="text"
                            value={recipientPublicKey}
                            onChange={handlePublicKeyChange}
                            placeholder="Recipient Public Key"
                        />
                        <button onClick={handleSendEncryptedSymmetricKey}>Send Encrypted Symmetric Key</button>
                        {messageStatus && <p>{messageStatus}</p>}
                    </div>
                    <div>
                        <h2>Enter Encrypted Symmetric Key</h2>
                        <input
                            type="text"
                            value={encryptedSymmetricKey}
                            onChange={(e) => setEncryptedSymmetricKey(e.target.value)}
                            placeholder="Enter Encrypted Symmetric Key"
                        />
                        <button onClick={handleDecryptSymmetricKey}>Decrypt Symmetric Key</button>
                    </div>
                    <div>
                        <h2>Chat</h2>
                        <Chat
                            recipientEmail={recipientEmail}
                            onReceiveMessage={handleReceiveMessage}
                            symmetricKey={symmetricKey}
                            user={user.email}
                        />
                        {encryptedMessage && <p>Decrypted Message: {encryptedMessage}</p>}
                    </div>
                </div>
            )}
        </div>
    );
};

export default Homepage;
