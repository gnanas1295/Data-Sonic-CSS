import tkinter as tk
from tkinter import messagebox
import requests
import logging

logging.basicConfig(level=logging.DEBUG)

SERVER_URL = 'http://127.0.0.1:5000/'

class SecureChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure Chat App")
        self.login_frame = tk.Frame(root)
        self.setup_login_frame()


    def setup_login_frame(self):
        self.login_frame.pack()
        logging.debug("Login frame setup completed")
        tk.Label(self.login_frame, text="Email:").grid(row=0, column=0)
        self.email_entry = tk.Entry(self.login_frame)
        self.email_entry.grid(row=0, column=1)
        tk.Label(self.login_frame, text="Password:").grid(row=1, column=0)
        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1)
        tk.Button(self.login_frame, text="Login", command=self.login).grid(row=2, column=0, columnspan=2)

    def show_login_frame(self):
        self.setup_login_frame()

    def login(self):
        logging.debug("Attempting login")
        email = self.email_entry.get()
        password = self.password_entry.get()
        response = requests.post(f'{SERVER_URL}/login', json={'email': email, 'password': password})
        if response.status_code == 200:
            messagebox.showinfo("Success", "Login successful")
        else:
            messagebox.showerror("Error", "Invalid credentials")


if __name__ == '__main__':
    root = tk.Tk()
    app = SecureChatApp(root)
