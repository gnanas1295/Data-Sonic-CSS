import base64
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Cipher import AES
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import dh

def generate_dh_keys():
    parameters = dh.generate_parameters(generator=2, key_size=2048)
    private_key = parameters.generate_private_key()
    public_key = private_key.public_key()
    return private_key, public_key

def serialize_public_key(public_key):
    serialized_key = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return base64.urlsafe_b64encode(serialized_key).decode('utf-8')

def deserialize_public_key(serialized_key):
    serialized_key = serialized_key.encode('utf-8')
    # Ensure the correct padding
    missing_padding = len(serialized_key) % 4
    if missing_padding:
        serialized_key += b'=' * (4 - missing_padding)
    decoded_key = base64.urlsafe_b64decode(serialized_key)
    return serialization.load_pem_public_key(decoded_key)

def compute_shared_secret(private_key, public_key):
    shared_secret = private_key.exchange(public_key)
    return shared_secret

def derive_session_key(shared_secret):
    salt = get_random_bytes(16)
    session_key = PBKDF2(shared_secret, salt, dkLen=32, count=1000000)
    return session_key

def encrypt_message(message, session_key):
    cipher = AES.new(session_key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(message.encode())
    return base64.urlsafe_b64encode(cipher.nonce + tag + ciphertext).decode()

def decrypt_message(encrypted_message, session_key):
    data = base64.urlsafe_b64decode(encrypted_message)
    nonce, tag, ciphertext = data[:16], data[16:32], data[32:]
    cipher = AES.new(session_key, AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag).decode()
