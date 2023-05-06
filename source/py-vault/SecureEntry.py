from __future__ import annotations
import pandas as pd
from PyVaultCrypto import PyVaultCrypto
from typing import Tuple
import pickle


class SecureEntry:
    # The constructor creates instance using persisted data
    def __init__(self, id, parent_id, name_hint_enc, name_hint_enc_iv, enc_data, enc_data_iv, hint_resp_hash, hint_resp_hash_salt, \
                hint_resp, pvc: PyVaultCrypto , parent_pvc: PyVaultCrypto) -> None:
        # DataFrame id
        self.id = id

        #Parent ID
        self.parent_id = parent_id

        # Name and Hint are encrypted using parent_pvc, while data and child_dict using pvc
        self._parent_pvc = parent_pvc

        # Hint Response Hash
        if pvc is not None:
            self._pvc = pvc
        else:
            # When loading from file, create pvc
            pvc = PyVaultCrypto(hint_resp, salt=hint_resp_hash_salt, iv=enc_data_iv)

        self.hint_resp_hash = hint_resp_hash
        self.hint_resp_hash_salt = hint_resp_hash_salt
        self.enc_data_iv = enc_data_iv
        self.enc_data = enc_data
        self.name_hint_enc = name_hint_enc
        self.name_hint_enc_iv = name_hint_enc_iv


    @staticmethod
    def get_schema():
        return {'id': None, 'parent_id': None, \
                'name_hint_enc': None, 'name_hint_enc_iv': None,  \
                'enc_data': None, 'enc_data_iv': None, \
                'hssh': None, 'salt': None}
    

    def get_persistent_data(self) -> dict:
        return {'id': self.id, 'parent_id': self.parent_id, \
                'name_hint_enc': self.name_hint_enc, 'name_hint_enc_iv': self.name_hint_enc_iv,  \
                'enc_data': self.enc_data, 'enc_data_iv': self.enc_data_iv, \
                'hssh': self.hint_resp_hash, 'salt': self.hint_resp_hash_salt}
    

    @classmethod
    def from_new_data(cls, id, parent_id, name, hint, hint_resp, data, parent_pvc: PyVaultCrypto) -> SecureEntry:
        # Hint Response Hash
        pvc = PyVaultCrypto(hint_resp)
        hint_resp_hash, hint_resp_hash_salt = pvc.get_pwd_hash()

        # Children dict - initially empty
        child_dict = {}

        # Encrypt name/hint using parent_pvc
        nhe, nhei, ed, edi = cls._encrypt(name, hint, data, child_dict, pvc, parent_pvc)

        return cls(id, parent_id, nhe, nhei, ed, edi, hint_resp_hash, hint_resp_hash_salt, hint_resp, pvc, parent_pvc)
    

    @classmethod
    def _encrypt(cls, name, hint, data, child_dict, pvc: PyVaultCrypto, parent_pvc: PyVaultCrypto):
        # Serialize to bytes, Encrypt and save
        name_hint_enc, name_hint_enc_iv = parent_pvc.encrypt(pickle.dumps((name, hint)))
        enc_data, enc_data_iv = pvc.encrypt(pickle.dumps((data, child_dict)))
        return name_hint_enc, name_hint_enc_iv, enc_data, enc_data_iv
    
    
    def _decrypt(self) -> Tuple(str, str, str, dict):
        # Decrypt and Convert back to Tuple format
        name, hint = pickle.loads(self._parent_pvc.decrypt(self.name_hint_enc, returnAsBytes=True))
        data, child_dict = pickle.loads(self._pvc.decrypt(self.enc_data, returnAsBytes=True))
        return name, hint, data, child_dict
    

    def auth(self, pwd):
        return self._pvc.verify_password(pwd)


    def child_exist(self, child_name):
        # Decrypt to get child_dict
        _, _, _, child_dict = self._decrypt()

        # Check if already exists
        if child_name in child_dict:
            return True
        else:
            return False


    def add_child(self, child: SecureEntry):
        # Decrypt to get child_dict
        name, hint, data, child_dict = self._decrypt()
            
        child_dict[child.get_content()[0]] = child.id
        self.name_hint_enc, self.name_hint_enc_iv, self.enc_data, self.enc_data_iv = self._encrypt(name, hint, data, child_dict, self._pvc, self._parent_pvc)


    def get_content(self):
        return self._decrypt()
    

    def get_pvc(self):
        # TODO: auth or else re-verify pwd
        return self._pvc