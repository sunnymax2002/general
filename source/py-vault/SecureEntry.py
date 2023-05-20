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
            if hint_resp is not None:
                # When loading from file, create pvc
                self._pvc = PyVaultCrypto(hint_resp, salt=hint_resp_hash_salt, iv=enc_data_iv)
            else:
                self._pvc = None

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
                'hint_resp_hash': None, 'hint_resp_hash_salt': None}
    

    def get_persistent_data(self) -> dict:
        return {'id': self.id, 'parent_id': self.parent_id, \
                'name_hint_enc': self.name_hint_enc, 'name_hint_enc_iv': self.name_hint_enc_iv,  \
                'enc_data': self.enc_data, 'enc_data_iv': self.enc_data_iv, \
                'hint_resp_hash': self.hint_resp_hash, 'hint_resp_hash_salt': self.hint_resp_hash_salt}


    @classmethod
    def from_dict(cls, se_dict: dict, hint_resp: str, parent_pvc: PyVaultCrypto) -> SecureEntry:
        #TODO: cross check se_dict against cls.get_schema()
        return cls(se_dict['id'], se_dict['parent_id'], se_dict['name_hint_enc'], se_dict['name_hint_enc_iv'], \
                   se_dict['enc_data'], se_dict['enc_data_iv'], se_dict['hint_resp_hash'], se_dict['hint_resp_hash_salt'], \
                    hint_resp, pvc=None, parent_pvc=parent_pvc)


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

        if self._pvc is not None:
            data, child_dict = pickle.loads(self._pvc.decrypt(self.enc_data, returnAsBytes=True))
        else:
            data = None
            child_dict = None
        
        return name, hint, data, child_dict
    

    def auth(self, pwd):
        # PVC to be initialized if se created without hint_resp
        if self._pvc is None:
            self._pvc = PyVaultCrypto(pwd, salt=self.hint_resp_hash_salt, iv=self.enc_data_iv)

        return self._pvc.verify_password(pwd)


    def has_child(self):
        # Decrypt to get child_dict
        _, _, _, child_dict = self._decrypt()

        # Check if already exists
        if len(child_dict) > 0:
            return True
        else:
            return False
        

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
        
        child_name, _, _, _ = child._decrypt()

        if child_name in child_dict:
            raise Exception("Child Entry with same name already exists")
        else:
            child_dict[child_name] = child.id
            a, b, c, d = self._encrypt(name, hint, data, child_dict, self._pvc, self._parent_pvc)
            self.name_hint_enc = a
            self.name_hint_enc_iv = b
            self.enc_data = c
            self.enc_data_iv = d

            # Debug code
            p, q, r, s = self._decrypt()
            assert (p == name and q == hint and r == data and s == child_dict)
            return child_dict


    def get_content(self):
        return self._decrypt()
    

    def get_pvc(self):
        # TODO: auth or else re-verify pwd
        return self._pvc