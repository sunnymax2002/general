from __future__ import annotations
import pandas as pd
from PyVaultCrypto import PyVaultCrypto
from typing import Tuple
import pickle

class SecureEntry:
    def __init__(self, id, parent_id, name_hint_enc, name_hint_enc_iv, enc_data, enc_data_iv, hint_resp_hash, hint_resp_hash_salt, parent_pvc: PyVaultCrypto) -> None:
        # DataFrame id
        self.id = id

        #Parent ID
        self.parent_id = parent_id

        # Name and Hint are encrypted using parent_pvc, while data and child_dict using pvc
        self._parent_pvc = parent_pvc

        # Hint Response Hash
        self._pvc = PyVaultCrypto.from_persistent_data(hint_resp_hash, hint_resp_hash_salt, enc_data_iv)
        self.hint_resp_hash = hint_resp_hash
        self.hint_resp_hash_salt = hint_resp_hash_salt



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
        _pvc = PyVaultCrypto(hint_resp)
        hint_resp_hash, hint_resp_hash_salt = _pvc.get_pwd_hash()

        # Children dict - initially empty
        child_dict = {}

        # Encrypt
        cls._encrypt(name, hint, data, child_dict)
    
    def _encrypt(self, name, hint, data, child_dict):
        # Serialize to bytes, Encrypt and save
        self.name_hint_enc, self.name_hint_enc_iv = self._parent_pvc.encrypt(pickle.dumps((name, hint)))
        self.enc_data, self.enc_data_iv = self._pvc.encrypt(pickle.dumps((data, child_dict)))
    
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
            
        child_dict[child.name] = child.id
        self._encrypt(name, hint, data, child_dict)

    def get_name(self):
        name, _, _, _ = self._decrypt()
        return name

class PyVault:
    def __init__(self, mpvc: PyVaultCrypto, root_idx: dict, df_se: pd.DataFrame, pkl_fpath: str) -> None:
        self.mpvc = mpvc
        self.root_idx = root_idx
        self.df_se = df_se
        self.pkl_fpath= pkl_fpath
        # The entry that has been unlocked and is currently active for use
        self.current_se = None

    @classmethod
    def _write_to_file(cls, pkl_fpath, mpwd_hash, mpwd_salt, mpvc_iv, enc_root_idx: bytes, df_se: pd.DataFrame):
        pass

    @classmethod
    def _read_from_file(cls, pkl_fpath):
        pass
        # return mpwd_hash, mpwd_salt, mpvc_iv, enc_root_idx, df_se

    @classmethod
    def from_new_data(cls, mpwd, pkl_fpath):
        mpvc = PyVaultCrypto(mpwd)
        df_se = pd.DataFrame(columns=SecureEntry.get_schema().keys())
        return cls(mpvc, {}, df_se, pkl_fpath)

    @classmethod
    def from_persistent_data(cls, pkl_fpath, mpwd):
        # Read persisted objects from pickle file
        mpwd_hash, mpwd_salt, mpvc_iv, enc_root_idx, df_se = cls._read_from_file(pkl_fpath)

        # Create master pvc
        mpvc = PyVaultCrypto.from_persistent_data(mpwd_hash, mpwd_salt, mpvc_iv, mpwd)

        # Decrypt root index
        root_idx = dict(mpvc.decrypt(enc_root_idx, returnAsBytes=True))
    
    @classmethod
    def _update_root_idx(cls, root_idx: dict, se: SecureEntry):
        if se.parent_id is not None:
            # not a root entry, nothing to do
            return
        
        name = se.get_name()
        if name not in root_idx.keys():
            root_idx[name] = se.id
        else:
            raise Exception("Root Entry with same name already exists")

    def add_entry(self, se: SecureEntry):
        # TODO: Check if already exists in df_se

        self._update_root_idx(se)


# df = pd.DataFrame(columns=SecureEntry.get_schema().keys())

# Create Master pvc, which is used to encrypt 'name-hint' for top-level SecureEntries
mpwd = 'master-pwd'
mpvc = PyVaultCrypto(mpwd)

pkl_fpath = r"C:\Users\sunny\My Drive (sbav2309@gmail.com)\Home and Life\Vault\pyvault.pkl"

py_vault = PyVault.from_new_data(mpwd, pkl_fpath)

cust_id = '123'
e1 = SecureEntry(1, None, 'hdfc', 'cust-id', cust_id, 'secret', mpvc)

id, pid, nhe, nhei, ed, edi, h, s = e1.get_persistent_data().values()

se_t = PyVaultCrypto.from_persistent_data(h, s, edi, cust_id)
print(se_t.decrypt(ed))

py_vault.add_entry(e1)

e2 = SecureEntry(2, 1, 'debit card', 'Last 4 digits of card', '9876', 'pin')
e3 = SecureEntry(3, 1, 'credit card', 'Last 4 digits of card', '5678', 'pin2')
e1.add_child(e2)
e1.add_child(e3)

entries = [e1.get_persistent_data(), e2.get_persistent_data(), e3.get_persistent_data()]

df = pd.DataFrame.from_dict(entries).set_index('id')

print(df)