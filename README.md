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

1. Navigate to the `secure-messaging-gmail` directory:

   ```sh
   cd secure_messaging
   ```

2. Open terminal: (For Mac)

   ```sh
   python -m venv venv
   source venv/bin/activate
   pip install Flask Flask-SQLAlchemy Flask-Mail cryptography
   python app.py
   ```
3. Open Command Prompt: (For Windows)

   ```sh
   python -m venv venv
   venv\Scripts\activate
   pip install Flask Flask-SQLAlchemy Flask-Mail cryptography requests nvm
   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
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
    cd secure_messaging
    rm -rf venv
    python -m venv venv
    source venv/bin/activate  # On Windows use venv\Scripts\activate
   ```

This setup provides a secure, end-to-end encrypted chatbot for a resort website with user-friendly authentication and a web-based interface.
