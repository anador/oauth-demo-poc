import base64
from cryptography.fernet import Fernet
import hashlib
import cryptography


def generate_key(secret: str) -> bytes:
    return base64.urlsafe_b64encode(hashlib.sha256(secret.encode()).digest())


def encrypt(data: str, secret: str) -> str:
    key = generate_key(secret)  # Generate key from secret
    cipher = Fernet(key)
    encrypted_data = cipher.encrypt(data.encode()) 
    return encrypted_data.decode()


def decrypt(encrypted_data: str, secret: str) -> str:
    try:
        key = generate_key(secret)  # Regenerate key from secret
        cipher = Fernet(key)
        decrypted_data = cipher.decrypt(encrypted_data.encode())
        return decrypted_data.decode()

    except cryptography.fernet.InvalidToken:
        raise ValueError("Decryption failed: Invalid or tampered data")
