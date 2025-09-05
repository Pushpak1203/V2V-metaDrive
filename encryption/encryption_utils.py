# encryption/encryption_utils.py

from cryptography.fernet import Fernet
import os

# Default key location (can be overridden by config/env)
DEFAULT_KEY_FILE = os.path.join(os.path.dirname(__file__), "secret.key")


def generate_key(path: str = DEFAULT_KEY_FILE):
    """
    Generates a new Fernet key and saves it to a file.
    """
    key = Fernet.generate_key()
    with open(path, "wb") as f:
        f.write(key)
    print(f"[ENCRYPTION] New key generated and saved at {path}")
    return key


def load_key(path: str = DEFAULT_KEY_FILE):
    """
    Loads an encryption key from file, generates one if missing.
    """
    if not os.path.exists(path):
        print(f"[ENCRYPTION] No key file found at {path}, generating new key...")
        return generate_key(path)
    with open(path, "rb") as f:
        return f.read()


# Global cipher instance
_KEY = load_key()
_CIPHER = Fernet(_KEY)


def encrypt_message(message: bytes) -> bytes:
    """
    Encrypts a message using Fernet.
    """
    return _CIPHER.encrypt(message)


def decrypt_message(token: bytes) -> bytes:
    """
    Decrypts a message using Fernet.
    """
    return _CIPHER.decrypt(token)

