# communication/encryption.py
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os


class EncryptionManager:
    def __init__(self, key_b64: str):
        """
        Initialize AES-GCM encryption with a base64 key.
        """
        key = base64.b64decode(key_b64)
        self.aesgcm = AESGCM(key)

    def encrypt(self, plaintext: bytes, associated_data: bytes = None) -> bytes:
        """
        Encrypts the message using AES-GCM.
        Returns nonce + ciphertext.
        """
        nonce = os.urandom(12)  # 96-bit nonce
        ciphertext = self.aesgcm.encrypt(nonce, plaintext, associated_data)
        return nonce + ciphertext

    def decrypt(self, data: bytes, associated_data: bytes = None) -> bytes:
        """
        Decrypts AES-GCM message.
        Expects nonce + ciphertext.
        """
        nonce, ciphertext = data[:12], data[12:]
        return self.aesgcm.decrypt(nonce, ciphertext, associated_data)
