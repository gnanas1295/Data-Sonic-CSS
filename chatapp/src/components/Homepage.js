import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { googleSignIn, googleSignOut } from '../utils/googleAuth';
import './Homepage.css';
import { getAuth, onAuthStateChanged } from 'firebase/auth';

const Homepage = () => {
    const [user, setUser] = useState(null);

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
        } catch (error) {
            console.error('Error logging out:', error);
        }
    };

    return (
        <div className="homepage">
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
                        <h2>Welcome, {user.email}</h2>
                        <Link to="/chat">Go to Chat</Link>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Homepage;
