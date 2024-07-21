import React from 'react';
import { googleSignIn } from '../utils/googleAuth';

const Login = () => {
    const handleLogin = async () => {
        try {
            const user = await googleSignIn();
            console.log('User:', user);
            // Handle user login, store user info, etc.
        } catch (error) {
            console.error('Login failed:', error);
        }
    };

    return (
        <div>
            <button onClick={handleLogin}>Login with Google</button>
        </div>
    );
};

export default Login;
