// utils/googleAuth.js

import { base64urlEncode } from './base64url';
import { initializeApp } from 'firebase/app';
import { getAuth, GoogleAuthProvider, signInWithPopup, signOut, setPersistence, browserLocalPersistence } from 'firebase/auth';

const firebaseConfig = {
    apiKey: process.env.REACT_APP_FIREBASE_API_KEY,
    authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN,
    projectId: process.env.REACT_APP_FIREBASE_PROJECT_ID,
    storageBucket: process.env.REACT_APP_FIREBASE_STORAGE_BUCKET,
    messagingSenderId: process.env.REACT_APP_FIREBASE_MESSAGING_SENDER_ID,
    appId: process.env.REACT_APP_FIREBASE_APP_ID,
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
setPersistence(auth, browserLocalPersistence);

export const googleSignIn = async () => {
    const provider = new GoogleAuthProvider();
    provider.addScope('https://www.googleapis.com/auth/gmail.send');
    try {
        const result = await signInWithPopup(auth, provider);
        const token = await result.user.getIdToken(true);
        return { user: result.user, token };
    } catch (error) {
        console.error('Error signing in with Google:', error);
        throw error;
    }
};

export const googleSignOut = async () => {
    try {
        await signOut(auth);
    } catch (error) {
        console.error('Error signing out:', error);
        throw error;
    }
};

export const sendEmail = async (recipientEmail, subject, body, token) => {
    const rawEmail = `To: ${recipientEmail}\nSubject: ${subject}\n\n${body}`;
    const encodedEmail = base64urlEncode(rawEmail);

    const response = await fetch('https://gmail.googleapis.com/gmail/v1/users/me/messages/send', {
        method: 'POST',
        headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            raw: encodedEmail,
        }),
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error.message);
    }

    return response.json();
};
