from __future__ import annotations
import pandas as pd
from PyVaultCrypto import PyVaultCrypto
from SecureEntry import SecureEntry
from typing import Tuple
import pickle
from os import path


class PyVault:
    def __init__(self, mpvc: PyVaultCrypto, root_idx: dict, df_se: pd.DataFrame, pkl_fpath: str, cb_GetUserPwd) -> None:
        self.mpvc = mpvc
        self.root_idx = root_idx
        self.df_se = df_se
        self.pkl_fpath= pkl_fpath

        # The entry that has been unlocked and is currently active for use
        self._current_se = None

        #Callback function handlers
        self._cb_GetUserPwd = cb_GetUserPwd

    @classmethod
    def _write_to_file(cls, pkl_fpath, mpwd_hash, mpwd_salt, mpvc_iv, enc_root_idx: bytes, df_se: pd.DataFrame):
        with open(pkl_fpath, 'wb') as wf:
            pickle.dump((mpwd_hash, mpwd_salt, mpvc_iv, enc_root_idx, df_se), wf)

    @classmethod
    def _read_from_file(cls, pkl_fpath):
        with open(pkl_fpath, 'rb') as rf:
            mpwd_hash, mpwd_salt, mpvc_iv, enc_root_idx, df_se = pickle.load(rf)
        return mpwd_hash, mpwd_salt, mpvc_iv, enc_root_idx, df_se


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

        return cls(mpvc, root_idx, df_se, pkl_fpath)
    
    @classmethod
    def _update_root_idx(cls, root_idx: dict, se: SecureEntry):
        if se.parent_id is not None:
            # not a root entry, nothing to do
            return
        
        name, _, _, _ = se.get_content()
        if name not in root_idx.keys():
            root_idx[name] = se.id
        else:
            raise Exception("Root Entry with same name already exists")

    def add_entry(self, se: SecureEntry):
        # TODO: Check if already exists in df_se

        self._update_root_idx(se)

    def find_entry(self, search_text) -> dict:
        '''At current level, searches and finds matching entries and reports dict(name, id)'''

        return {}
    

    def _check_open_entry(self, id):
        #TODO: Check if entry is child of open parent

        self.df_se[self.df_se.index == id]


    def open_entry(self, id):
        '''Opens the entry with id, the parent of id must be open or else throws an error'''

        # Fetch the entry from df
        se = self._check_open_entry(id)

        # Get pwd to open the entry
