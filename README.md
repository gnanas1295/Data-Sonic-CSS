# Secure Chatbot

This project is a secure chat application that uses end-to-end encryption to ensure the privacy and security of messages exchanged between users. The application features user authentication through social media and email verification, and a web-based user interface for ease of use.

## Project Structure

```
secure_messaging/
│── static/
│   |── scripts.js
|   |── styles.css
│
├── templates/
│   |── index.html
|__ app.py
│
├──.gitignore
│
└── README.md
```

## Getting Started

1. Navigate to the `backend` directory:

   ```sh
   cd backend
   ```

2. Open terminal: (For Mac)
    For running Backend server
   ```sh
   python -m venv venv
   source venv/bin/activate
   pip install Flask Flask-SQLAlchemy Flask-Mail cryptography requests nvm
   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client flask-cors gunicorn
   python app.py
   ```
3. Open Command Prompt: (For Windows)
   For running Backend server
   ```sh
   python -m venv venv
   venv\Scripts\activate
   pip install Flask Flask-SQLAlchemy Flask-Mail cryptography requests nvm
   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client flask-cors gunicorn
   python app.py
   ```
   
4. Note:

    We use Google Auth for the authentication of the users. So, the API keys of your Google OAuth should be added in the created python virtual environment, before running the app.py file. If not, error will arise.
    ```
    For Mac:
    export SECRET_KEY="your_secret_key_here"
    export GOOGLE_CLIENT_ID="your_google_client_id_here"
    export GOOGLE_CLIENT_SECRET="your_google_client_secret_here"

    For Windows:
    set SECRET_KEY=your_secret_key_here
    set GOOGLE_CLIENT_ID=your_google_client_id_here
    set GOOGLE_CLIENT_SECRET=your_google_client_secret_here
    ```
5. Open terminal: (For Mac)
    For running Frontend
   ```
   cd chatapp
   nvm use 18
   npm install
   npm start
   ```
6. Open Command Prompt: (For Windows)
   For running Frontend
   ```
   cd chatapp
   nvm use 18
   npm install
   npm start
   ```

   
## Features

- **User Authentication**: Users can authenticate via social media (Google) or email.
- **End-to-End Encryption**: Messages are encrypted using Diffie-Hellman key exchange and AES encryption.
- **Email Verification**: New users must verify their email address during registration.
- **Web-Based UI**: The application provides a web-based interface for chatting with the resort bot.

## Security Considerations

- **End-to-End Encryption**: Ensures that messages can only be read by the intended recipient.
- **OAuth Authentication**: Uses secure OAuth protocol for social media authentication.
- **Email Verification**: Adds an extra layer of security by verifying users' email addresses.
- **Session Keys**: Derived using PBKDF2 with a high iteration count to ensure security.

## Future Improvements

- **Two-Factor Authentication**: Adding an extra layer of security.
- **Improved Error Handling**: More robust error handling and user feedback.
- **Group Chats**: Extending functionality to support group communications.


If you already have a virtual environment, remove it and create a new one to ensure a clean installation of dependencies.

 ```sh
    python -m venv venv
   venv\Scripts\activate
   pip install Flask Flask-SQLAlchemy Flask-Mail cryptography requests nvm
   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client flask-cors gunicorn
   python app.py
   ```

This setup provides a secure, end-to-end encrypted chatbot for a resort website with user-friendly authentication and a web-based interface.

Important info about each files:
FE Files:

1) App.js -> Main Entry Sets up routing for different components (e.g., ChatPage, Login, Homepage) using React Router

2) ChatPage.js -> Manages the chat interface where users send and receive messages (Displays chat interface.
Handles sending and receiving messages.
Encrypts messages before sending using the symmetric key.
Decrypts received messages using the symmetric key.)
(Communicates with backend to send and receive encrypted messages), THis internally uses chat.js to provide the interface for the user interaction.

3) Chat.js -> that focuses on the user interface for sending and receiving messages (Rendering Chat Interface: It provides the user interface for typing and sending messages.
Encrypting Messages: It encrypts messages using the provided symmetric key before sending them.
Displaying Status: It displays the status of message sending (e.g., success or error).

4) Homepage.js -> Displays the homepage of the application (Typically would provide navigation to login or chat pages.)

5) Login.js -> Manages user login via Google authentication. (Redirects authenticated users to ChatPage.)

6) cryptoUtils.js -> Provides cryptographic utilities for the frontend, Generates symmetric keys (AES).and Generates RSA key pairs

Backend:

1) app.py -> Backend server handling key exchange and message storage

DB:

2) messages.db -> SQLite database storing user messages and keys
