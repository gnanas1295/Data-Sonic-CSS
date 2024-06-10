import os
import tkinter as tk
from tkinter import messagebox
import requests
import logging
import base64
from cryptography.hazmat.primitives import serialization
from encryption import generate_dh_keys, compute_shared_secret, derive_session_key, encrypt_message, decrypt_message, serialize_public_key

logging.basicConfig(level=logging.DEBUG)

SERVER_URL = os.environ.get('SERVER_URL', 'http://127.0.0.1:5000')

class SecureChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure Chat App")
        self.login_frame = tk.Frame(root)
        self.register_frame = tk.Frame(root)
        self.chat_frame = tk.Frame(root)

        self.setup_login_frame()

    def setup_login_frame(self):
        self.clear_frames()
        self.login_frame.pack()
        logging.debug("Login frame setup completed")
        tk.Label(self.login_frame, text="Email:").grid(row=0, column=0)
        self.email_entry = tk.Entry(self.login_frame)
        self.email_entry.grid(row=0, column=1)
        tk.Label(self.login_frame, text="Password:").grid(row=1, column=0)
        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1)
        tk.Button(self.login_frame, text="Login", command=self.login).grid(row=2, column=0, columnspan=2)
        tk.Button(self.login_frame, text="Register", command=self.show_register_frame).grid(row=3, column=0, columnspan=2)

    def setup_register_frame(self):
        self.clear_frames()
        self.register_frame.pack()
        logging.debug("Register frame setup completed")
        tk.Label(self.register_frame, text="Email:").grid(row=0, column=0)
        self.reg_email_entry = tk.Entry(self.register_frame)
        self.reg_email_entry.grid(row=0, column=1)

        tk.Label(self.register_frame, text="Username:").grid(row=1, column=0)
        self.username_entry = tk.Entry(self.register_frame)
        self.username_entry.grid(row=1, column=1)

        tk.Label(self.register_frame, text="Password:").grid(row=2, column=0)
        self.reg_password_entry = tk.Entry(self.register_frame, show="*")
        self.reg_password_entry.grid(row=2, column=1)

        tk.Button(self.register_frame, text="Register", command=self.register).grid(row=3, column=0, columnspan=2)
        tk.Button(self.register_frame, text="Back to Login", command=self.show_login_frame).grid(row=4, column=0, columnspan=2)

    def show_login_frame(self):
        self.setup_login_frame()

    def show_register_frame(self):
        self.setup_register_frame()

    def login(self):
        logging.debug("Attempting login")
        email = self.email_entry.get()
        password = self.password_entry.get()
        try:
            response = requests.post(f'{SERVER_URL}/login', json={'email': email, 'password': password})
            response.raise_for_status()
            messagebox.showinfo("Success", "Login successful")
            self.setup_chat_frame()
        except requests.exceptions.HTTPError as err:
            logging.error(f"HTTP error occurred: {err}")
            messagebox.showerror("Error", "Invalid credentials")
        except requests.exceptions.RequestException as err:
            logging.error(f"Request error occurred: {err}")
            messagebox.showerror("Error", "A network error occurred")

    def register(self):
        logging.debug("Attempting registration")
        email = self.reg_email_entry.get()
        username = self.username_entry.get()
        password = self.reg_password_entry.get()
        try:
            response = requests.post(f'{SERVER_URL}/register', json={'email': email, 'username': username, 'password': password})
            response.raise_for_status()
            messagebox.showinfo("Success", "Registration successful, please verify your email")
        except requests.exceptions.HTTPError as err:
            logging.error(f"HTTP error occurred: {err}")
            try:
                messagebox.showerror("Error", response.json()['message'])
            except ValueError:
                messagebox.showerror("Error", "A server error occurred")
        except requests.exceptions.RequestException as err:
            logging.error(f"Request error occurred: {err}")
            messagebox.showerror("Error", "A network error occurred")

    def setup_chat_frame(self):
        self.clear_frames()
        self.chat_frame.pack()
        logging.debug("Chat frame setup completed")
        tk.Label(self.chat_frame, text="Recipient:").grid(row=0, column=0)
        self.recipient_entry = tk.Entry(self.chat_frame)
        self.recipient_entry.grid(row=0, column=1)

        tk.Label(self.chat_frame, text="Message:").grid(row=1, column=0)
        self.message_entry = tk.Entry(self.chat_frame)
        self.message_entry.grid(row=1, column=1)

        tk.Button(self.chat_frame, text="Send", command=self.send_message).grid(row=2, column=0, columnspan=2)
        tk.Button(self.chat_frame, text="Receive", command=self.receive_messages).grid(row=3, column=0, columnspan=2)

    # hide all frames before showing a new one
    def clear_frames(self):
        self.login_frame.pack_forget()
        self.register_frame.pack_forget()
        self.chat_frame.pack_forget()

    def send_message(self):
        logging.debug("Attempting to send message")
        recipient = self.recipient_entry.get()
        message = self.message_entry.get()
        # Implement encryption here
        encrypted_message = encrypt_message(message, self.session_key)
        response = requests.post(f'{SERVER_URL}/send_message', json={'sender': self.username, 'recipient': recipient, 'message': encrypted_message})
        if response.status_code == 201:
            messagebox.showinfo("Success", "Message sent")
        else:
            messagebox.showerror("Error", response.json()['message'])

    def receive_messages(self):
        logging.debug("Attempting to receive messages")
        response = requests.get(f'{SERVER_URL}/receive_messages/{self.username}')
        if response.status_code == 200:
            messages = response.json()
            for msg in messages:
                # Implement decryption here
                decrypted_message = decrypt_message(msg['message'], self.session_key)
                messagebox.showinfo(f"Message from {msg['sender']}", decrypted_message)


    def perform_dh_key_exchange(self):
        logging.debug("Performing Diffie-Hellman key exchange")
        # Generate Diffie-Hellman keys
        self.private_key, self.public_key = generate_dh_keys()
        # Serialize the public key
        serialized_public_key = serialize_public_key(self.public_key)
        # Send serialized public key to server
        response = requests.post(f'{SERVER_URL}/dh_key_exchange', data={'public_key': serialized_public_key})
        print("Diffie-Hellman key exchange initiated")
        if response.status_code == 200:
            # Receive server's public key
            server_public_key = response.json()['public_key'].strip()  # Trim whitespace
            try:
                # Deserialize server's public key
                server_public_key = serialization.load_pem_public_key(base64.b64decode(server_public_key))
                # Compute shared secret
                shared_secret = compute_shared_secret(self.private_key, server_public_key)
                # Derive session key
                self.session_key = derive_session_key(shared_secret)
                logging.debug("Session key derived successfully")
            except Exception as e:
                logging.error(f"Error in Diffie-Hellman key exchange: {e}")
        else:
            logging.error("Error in Diffie-Hellman key exchange")

# Usage
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    root = tk.Tk()
    app = SecureChatApp(root)
    # Perform Diffie-Hellman key exchange before starting the Tkinter main loop
    app.perform_dh_key_exchange()
    root.mainloop()
