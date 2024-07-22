import React, { useState } from 'react';
import { googleSignIn, sendEmail } from '../utils/googleAuth';
import { generateKeyPair, encryptWithPublicKey } from '../utils/cryptoUtils';

const SendEmail = () => {
    const [email, setEmail] = useState('');
    const [publicKey, setPublicKey] = useState('');
    const [messageStatus, setMessageStatus] = useState('');
    const [user, setUser] = useState(null);
    const [token, setToken] = useState('');

    const handleLogin = async () => {
        try {
            const result = await googleSignIn();
            setUser(result.user);
            setToken(result.token); // Store the OAuth2 token
        } catch (error) {
            console.error('Error logging in:', error);
        }
    };

    const handleSendEmail = async () => {
        if (!user || !token) {
            setMessageStatus('Please log in first.');
            return;
        }

        console.log(user,token)

        // Generate key pair
        const { publicKey: senderPublicKey, privateKey } = generateKeyPair();
        setPublicKey(senderPublicKey);

        // Encrypt the secret key
        const secretKey = 'your-secret-key'; // Replace with your actual secret key
        const encryptedSecretKey = encryptWithPublicKey(secretKey, senderPublicKey);

        // Compose the email
        const subject = 'Your Encrypted Key';
        const body = `Here is the encrypted secret key:\n\n${encryptedSecretKey}\n\nVisit the following link to access the chat:\nhttp://localhost:3000/`;

        // Send email
        try {
            await sendEmail(email, subject, body, token);
            setMessageStatus('Email sent successfully.');
        } catch (error) {
            console.error('Error sending email:', error);
            setMessageStatus('Error sending email.');
        }
    };

    return (
        <div>
            {!user ? (
                <div>
                    <p>Please log in to send an email.</p>
                    <button onClick={handleLogin}>Login with Google</button>
                </div>
            ) : (
                <div>
                    <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="Recipient Email"
                    />
                    <button onClick={handleSendEmail}>Send Email</button>
                </div>
            )}
            {messageStatus && <p>{messageStatus}</p>}
        </div>
    );
};

export default SendEmail;
