import os
# import uuid
# import hashlib
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from datetime import datetime, timedelta

class PyVaultCrypto:
    def __init__(self, pwd: str, salt=None, iv=None):
        # Save hashed password and salt used for hashing
        self.hash, self.salt = self._get_hash(pwd, salt=salt)

        # Init cipher and iv (iv is salt used for creating cipher)
        self.cipher, self.iv = self._init_cipher(pwd, iv=iv)

        # Capture last auth time
        self.last_auth_time = datetime.now()

    @classmethod
    def from_persistent_data(cls, hash, salt, iv, pwd):
        kdf = cls._get_kdf(salt)
        try:
            # Check if pwd correct for given hash
            kdf.verify(str.encode(pwd), hash)

            # Construct cls instance
            return cls(pwd=pwd, salt=salt, iv=iv)
        except:
            raise Exception("Incorrect password")

    @classmethod
    def _get_salt(cls):
        # Generate salt, so that hash of text is unique even if text is common
        # return uuid.uuid4().hex
        return os.urandom(16)

    @classmethod
    def _get_kdf(cls, salt):
        return PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=480000)
    
    @classmethod
    def _get_hash(cls, pwd: str, salt=None):
        if salt is None:
            salt = cls._get_salt()

        kdf = cls._get_kdf(salt)
        return kdf.derive(str.encode(pwd)), salt
    
    @classmethod
    def _init_cipher(cls, pwd: str, iv=None):
        if iv is None:
            iv = cls._get_salt()

        kdf = cls._get_kdf(iv)
        key = kdf.derive(str.encode(pwd))

        return Cipher(algorithms.AES(key), modes.CTR(iv)), iv

    def verify_password(self, pwd: str):
        kdf = self._get_kdf(self.salt)
        # Below throws Exception, wrap and return True/False
        try:
            kdf.verify(str.encode(pwd), self.hash)
    
            # Capture last auth time
            self.last_auth_time = datetime.now()

            return True
        except:
            return False
        
    def get_pwd_hash(self):
        return self.hash, self.salt
    

    def _check_auth_timeout(self):
        return True
        #TODO: enable after testing complete
        if self.last_auth_time.timestamp() >= (datetime.now() - timedelta(minutes=1)).timestamp():
            return True
        else:
            return False
    

    def encrypt(self, pt):
        if not self._check_auth_timeout():
            raise Exception("Authentication timed out")
        
        encryptor = self.cipher.encryptor()

        # If pt is string, encode to bytes
        if isinstance(pt, str):
            data = str.encode(pt)
        elif isinstance(pt, bytes):
            # Assumed its byte array, how to check
            data = pt
        else:
            raise TypeError('Can encrypt only of type str or bytes')
        
        ct = encryptor.update(data) + encryptor.finalize()
        return ct, self.iv
    
    def decrypt(self, ct, returnAsBytes=False):
        if not self._check_auth_timeout():
            raise Exception("Authentication timed out")

        decryptor = self.cipher.decryptor()
        dt = decryptor.update(ct) + decryptor.finalize()
        if returnAsBytes:
            return dt
        else:
            return dt.decode()