# communication/encryption.py

import base64
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


class EncryptionManager:
    def __init__(self, config: dict):
        self.enabled = config.get("encryption", {}).get("enabled", False)
        self.algorithm = config.get("encryption", {}).get("algorithm", "AES")
        self.mode = config.get("encryption", {}).get("mode", "CBC")

        key_b64 = config.get("encryption", {}).get("key")

        if self.enabled:
            if not key_b64 or not isinstance(key_b64, str):
                raise ValueError("[ENCRYPTION] Invalid encryption key in v2v_settings.yaml (must be Base64 string).")

            try:
                self.key = base64.b64decode(key_b64)
            except Exception as e:
                raise ValueError(f"[ENCRYPTION] Failed to decode Base64 key: {e}")

            if len(self.key) not in [16, 24, 32]:
                raise ValueError("[ENCRYPTION] AES key length must be 16, 24, or 32 bytes.")

            print(f"[ENCRYPTION] AES key loaded successfully ({len(self.key) * 8}-bit).")
        else:
            self.key = None
            print("[ENCRYPTION] Disabled in configuration.")

    def encrypt(self, data: bytes) -> bytes:
        if not self.enabled:
            return data

        if self.algorithm != "AES":
            raise NotImplementedError("[ENCRYPTION] Only AES supported right now.")

        iv = os.urandom(16)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        encrypted = cipher.encrypt(pad(data, AES.block_size))
        return iv + encrypted  # Prepend IV for decryption

    def decrypt(self, data: bytes) -> bytes:
        if not self.enabled:
            return data

        iv = data[:16]
        encrypted_data = data[16:]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(encrypted_data), AES.block_size)
