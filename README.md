# Secure Chatbot

This project is a secure chat application that uses end-to-end encryption to ensure the privacy and security of messages exchanged between users. The application features user authentication through social media and email verification, and a web-based user interface for ease of use.

## Project Structure

```
secure_messaging/
│
├── static/
│   |── index.html
|__ app.py
│
├──.gitignore
│
└── README.md
```

## Getting Started

1. Navigate to the `secure_messaging` directory:

   ```sh
   cd secure_messaging
   ```

2. Open terminal:

   ```sh
   python3 app.py
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
    pip install --upgrade pip
    pip install -r requirements.txt
   ```

This setup provides a secure, end-to-end encrypted chatbot for a resort website with user-friendly authentication and a web-based interface.
