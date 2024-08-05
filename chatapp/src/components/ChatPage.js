import React, { useState, useEffect } from 'react';
import Chat from './Chat';
import './ChatPage.css';
import axios from 'axios';
import { getAuth, onAuthStateChanged } from 'firebase/auth';
import { generateKeyPair, encryptWithPublicKey, decryptWithPrivateKey, generateSymmetricKey, decryptWithSymmetricKey } from '../utils/cryptoUtils';
import { sendEmail } from '../utils/SendEmail';
import { googleSignIn, googleSignOut } from '../utils/googleAuth';

const ChatPage = () => {
    const [publicKey, setPublicKey] = useState('');
    const [privateKey, setPrivateKey] = useState('');
    const [recipientPublicKey, setRecipientPublicKey] = useState('');
    const [messageStatus, setMessageStatus] = useState('');
    const [user, setUser] = useState(null);
    const [recipientEmail, setRecipientEmail] = useState('');
    const [encryptedSymmetricKey, setEncryptedSymmetricKey] = useState('');
    const [symmetricKey, setSymmetricKey] = useState('');
    const [messages, setMessages] = useState([]);
    const [fetchingMessages, setFetchingMessages] = useState(false); // Flag to control message fetching
    console.log(messages)

    useEffect(() => {
        const auth = getAuth();
        onAuthStateChanged(auth, (user) => {
            if (user) {
                setUser(user);
                // Generate keys only if needed
                const { publicKey: userPublicKey, privateKey: userPrivateKey } = generateKeyPair();
                setPublicKey(userPublicKey);
                setPrivateKey(userPrivateKey);
            } else {
                setUser(null);
            }
        });
    }, []);

    useEffect(() => {
        if (user && recipientEmail && symmetricKey) {
            // Fetch messages immediately when conditions are met
            fetchMessages();

            // Set up periodic fetching
            const intervalId = setInterval(() => {
                fetchMessages();
            }, 5000); // Fetch every 5 seconds

            // Cleanup interval on component unmount or dependencies change
            return () => clearInterval(intervalId);
        }
    }, [user, recipientEmail, symmetricKey]);

    const fetchMessages = async () => {
        if (fetchingMessages) return; // Prevent overlapping fetches
        setFetchingMessages(true);

        try {
            const response = await axios.get('http://127.0.0.1:5000/get-messages', {
                params: {
                    recipient: recipientEmail,
                    sender: user.email
                }
            });

            console.log('Fetched messages:', response.data.messages);  // Debug log

            const decryptedMessages = response.data.messages.map(msg => {
                if (!msg.message) {
                    console.warn('Skipping message with missing content:', msg);
                    return { sender: msg.sender, message: 'Message content missing' };
                }

                try {
                    const decryptedMessage = decryptWithSymmetricKey(msg.message, symmetricKey);
                    return { sender: msg.sender, message: decryptedMessage };
                } catch (error) {
                    console.error('Error decrypting message:', error);
                    return { sender: msg.sender, message: 'Error decrypting message' };
                }
            });

            setMessages(decryptedMessages);
        } catch (error) {
            console.error('Error fetching messages:', error);
        } finally {
            setFetchingMessages(false); // Reset the flag
        }
    };

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
        } catch (error) {
            console.error('Error logging out:', error);
        }
    };

    const handleSendPublicKey = async () => {
        if (!user || !recipientEmail || !publicKey) {
            setMessageStatus('Please log in and provide recipient email.');
            return;
        }

        const subject = 'Your Public Key';
        const body = `Here is my public key:\n\n${publicKey}\n\nPlease use this public key to encrypt messages or symmetric keys for me.`;

        try {
            await sendEmail(recipientEmail, subject, body);
            setMessageStatus('Public key sent via email.');
        } catch (error) {
            setMessageStatus('Failed to send public key.');
        }
    };

    const handleSendEncryptedSymmetricKey = async () => {
        if (!user || !recipientPublicKey) {
            setMessageStatus('Please log in and provide recipient public key.');
            return;
        }

        const secretKey = generateSymmetricKey();
        const encryptedSecretKey = encryptWithPublicKey(secretKey, recipientPublicKey);

        const subject = 'Your Encrypted Symmetric Key';
        const body = `Here is the encrypted symmetric key:\n\n${encryptedSecretKey}\n\nVisit the following link to access the chat:\nhttp://localhost:3000/chat`;

        try {
            await sendEmail(recipientEmail, subject, body);
            setEncryptedSymmetricKey(encryptedSecretKey);
            setMessageStatus('Encrypted symmetric key sent via email.');
        } catch (error) {
            setMessageStatus('Failed to send encrypted symmetric key.');
        }
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
            fetchMessages(); // Fetch messages after key is decrypted
        } catch (error) {
            console.error('Error decrypting symmetric key:', error);
            setMessageStatus('Error decrypting symmetric key.');
        }
    };

    const handleSendMessage = async (encryptedMessage) => {
        if (!user || !symmetricKey) {
            setMessageStatus('No symmetric key available for encryption.');
            return;
        }
        try {
            await axios.post('http://127.0.0.1:5000/send-message', {
                recipient: recipientEmail,
                sender: user.email,
                encrypted_message: encryptedMessage
            });
            // Fetch messages after sending
            fetchMessages();
        } catch (error) {
            console.error('Error sending message:', error);
        }
    };

    const handlePublicKeyChange = (e) => {
        setRecipientPublicKey(e.target.value);
    };

    return (
        <div className="chat-page">
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
                        <Chat
                            recipientEmail={recipientEmail}
                            onReceiveMessage={handleSendMessage}
                            symmetricKey={symmetricKey}
                        />
                        <div>
                            <h2>Chat History</h2>
                            {messages.map((msg, index) => (
                                <div key={index}>
                                    <p><strong>{msg.sender}:</strong> {msg.message}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ChatPage;
