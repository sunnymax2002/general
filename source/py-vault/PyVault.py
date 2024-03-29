from __future__ import annotations
import pandas as pd
from PyVaultCrypto import PyVaultCrypto
from SecureEntry import SecureEntry
from typing import Tuple
import pickle
from os import path
from typing import Dict
import traceback


class PyVault:
    def __init__(self, mpvc: PyVaultCrypto, root_idx: dict, df_se: pd.DataFrame, pkl_fpath: str) -> None:
        self.mpvc = mpvc
        self.root_idx = root_idx
        self.df_se = df_se
        self.pkl_fpath= pkl_fpath

        self._reset_non_persistent_fields()


    @classmethod
    def _read_from_file(cls, pkl_fpath):
        with open(pkl_fpath, 'rb') as rf:
            mpwd_hash, mpwd_salt, mpvc_iv, enc_root_idx, df_se = pickle.load(rf)

        return mpwd_hash, mpwd_salt, mpvc_iv, enc_root_idx, df_se


    @classmethod
    def from_new_data(cls, mpwd, pkl_fpath):
        mpvc = PyVaultCrypto(mpwd)
        df_se = pd.DataFrame(columns=SecureEntry.get_schema().keys())
        df_se.set_index(['id'], inplace=True)
        return cls(mpvc, {}, df_se, pkl_fpath)


    @classmethod
    def from_persistent_data(cls, pkl_fpath, mpwd):
        # Read persisted objects from pickle file
        mpwd_hash, mpwd_salt, mpvc_iv, enc_root_idx, df_se = cls._read_from_file(pkl_fpath)

        # Create master pvc
        mpvc = PyVaultCrypto.from_persistent_data(mpwd_hash, mpwd_salt, mpvc_iv, mpwd)

        # Decrypt root index
        objs = mpvc.decrypt(enc_root_idx, returnAsBytes=True)
        root_idx= pickle.loads(objs)

        return cls(mpvc, root_idx, df_se, pkl_fpath)
    

    @classmethod
    def _update_root_idx(cls, root_idx: dict, se: SecureEntry):
        if se.parent_id is not None:
            # not a root entry, nothing to do
            return
        
        name, _, _, _ = se.get_content()
        if name not in root_idx.keys():
            root_idx[name] = se.id
            return root_idx
        else:
            raise Exception("Root Entry with same name already exists")


    def _write_to_file(self):
        with open(self.pkl_fpath, 'wb') as wf:
            objs = pickle.dumps(self.root_idx)
            enc_root_idx, _ = self.mpvc.encrypt(objs)   # Encrypt root_idx dict using pickle
            pickle.dump((self.mpvc.hash, self.mpvc.salt, self.mpvc.iv, enc_root_idx, self.df_se), wf)


    def _reset_non_persistent_fields(self):
        # The entry that has been unlocked and is currently active for use
        self._current_se: SecureEntry = None
        # Tree of entries opened
        self._opened_tree: Dict[int, SecureEntry] = {}


    def _get_new_id(self):
        if self.df_se.empty:
            return 0
        else:
            # Check df_se for max ID and assign new
            return max(self.df_se.index) + 1
        

    def _add_to_df(self, se: SecureEntry):
        # Check if exists in df
        if se.id in self.df_se.index:
            # self.df_se.loc[self.df_se.index == se.id].update(pd.DataFrame(se.get_persistent_data(), index=['id']))
            # self.df_se.update(pd.DataFrame(se.get_persistent_data(), index=['id']))

            # t = self.df_se['enc_data']
            # self.df_se.drop(self.df_se[self.df_se.index == se.id].index, inplace=True)

            # Get data and remove id field since it is index in df
            data = se.get_persistent_data()
            data.pop('id')
            # Update row: TODO: why can't it work as a single assignment: self.df_se.loc[self.df_se.index == se.id] = data
            for k, v in data.items():
                self.df_se.loc[self.df_se.index == se.id, k] = v

            # r = self.df_se['enc_data']
            # print(t)
            # print(r)
        else:
            # Add to df as new entry
            self.df_se.loc[len(self.df_se.index)] = se.get_persistent_data()


    def add_entry(self, n, h, hr, d, setAsCurrent=False):
        if self._current_se is None:
            # Adding root entry
            se = SecureEntry.from_new_data(self._get_new_id(), None, n, h, hr, d, self.mpvc)
            # TODO: Check if already exists in df_se
            self.root_idx = self._update_root_idx(root_idx=self.root_idx, se=se)
            self._add_to_df(se)
        else:
            se = SecureEntry.from_new_data(self._get_new_id(), self._current_se.id, n, h, hr, d, self._current_se.get_pvc())
            self._current_se.add_child(se)
            self._add_to_df(se)
            self._add_to_df(self._current_se)

        # Write to file
        self._write_to_file()

        if setAsCurrent:
            self._current_se = se

        # Update opened_tree
        self._opened_tree[se.id] = se


    def find_entry(self, search_text) -> dict:
        '''At current level, searches and finds matching entries and reports dict(name, id)'''

        if self._current_se is None:
            # Search in root
            search_dict = self.root_idx.items()
        else:
            _, _, _, s = self._current_se.get_content()
            search_dict = s.items()
            
        if search_dict is not None:
            return {key:val for (key, val) in search_dict if search_text in key}
        else:
            return {}


    def get_name_hint_by_id(self, id):
        # Check if part of opened tree
        if id in self._opened_tree:
            n, h, _, _ = self._opened_tree[id].get_content()
            return n, h
        else:
            return None, None


    def get_entry_securecontent(self, id, pwd: str):
        # Check if part of opened tree
        if id in self._opened_tree:
            # Auth
            se = self._opened_tree[id]
            try:
                se.auth(pwd)
                _, _, sc, _ = se.get_content()
                return sc
            except Exception:
                traceback.print_exc()
                return None
        else:
            return None


    def curr_entry_has_child(self):
        if self._current_se is not None:
            if self._current_se._pvc is not None:
                return self._current_se.has_child()
        else:
            # If at root, is mpvc valid?
            if self.mpvc is not None:
                return (len(self.root_idx) > 0)


    def open_entry(self, id, pwd=None, setAsCurrent=False) -> bool:
        '''Opens the entry with id (it is required that the parent of id must be open). If success, returns True else False'''

        # Check if entry already open
        if id in self._opened_tree:
            self._current_se = self._opened_tree[id]
            # Clear lower level entries from opened_tree
            keys = list(self._opened_tree.keys())
            lidx = keys.index(id)
            keys_to_remove = keys[lidx + 1:]
            for k in keys_to_remove:
                self._opened_tree.pop(k)

            # return self._current_se
            return True

        # If entry not open
        if id in self.df_se.index:
            # Assumed a single row shall be returned since id is unique key
            se_dict = self.df_se.loc[self.df_se.index == id].iloc[0].to_dict()

            if se_dict is not None:
                # Check if parent is in entry_tree?
                p_id = se_dict['parent_id']
                if p_id is None:
                    # Root entry, use mpvc
                    parent_pvc = self.mpvc
                elif p_id in self._opened_tree:
                    # Get parent_pvc
                    parent_pvc = self._opened_tree[p_id].get_pvc()
                else:
                    return False
                
                # Since id is index column, it is omitted, so add back
                se_dict['id'] = id
                se = SecureEntry.from_dict(se_dict, hint_resp=None, parent_pvc=parent_pvc)
        else:
            return False

        # Auth if pwd provided
        if pwd is not None:
            se.auth(pwd)
        
        # Update opened tree
        self._opened_tree[se.id] = se

        if setAsCurrent:
            self._current_se = se

        return True
    

    def get_entry_tree(self):
        # '''Returns a Tree of entries with current entry at the bottom, and root at top'''

        tree_dict = {'0 - Root': None}
        lvl = 1
        for se in self._opened_tree.values():
            n, _, _, _ = se.get_content()
            tree_dict['{0} - {1}'.format(lvl, n)] = se.id
            lvl += 1

        return tree_dict
    

    def close_all(self):
        self._reset_non_persistent_fields()


    def is_curr_entry_unlocked(self) -> bool:
        if self._current_se is not None:
            if self._current_se._pvc is not None:
                return True
        else:
            # If at root, is mpvc valid?
            if self.mpvc is not None:
                return True
        
        return False
    

    def has_curr_entry_changed(self, n, h, hr, d):
        # TODO: add logic - might not be necessary unless some security concern in updating without checking
        return True
    

    def update_curr_entry(self, n, h, hr, d) -> bool:
        if self._current_se is not None:
            # Create new curr_entry
            id = self._current_se.id
            parent_pvc = self._current_se._parent_pvc
            p_id = self._current_se.parent_id
            n_se = SecureEntry.from_new_data(id, p_id, n, h, hr, d, parent_pvc)

            # Debug only
            oe = self._current_se
            ed = oe.enc_data == n_se.enc_data
            edi = oe.enc_data_iv == n_se.enc_data_iv
            nhe = oe.name_hint_enc == n_se.name_hint_enc
            nhei = oe.name_hint_enc_iv == n_se.name_hint_enc_iv
            hrh = oe.hint_resp_hash == n_se.hint_resp_hash
            hrhs = oe.hint_resp_hash_salt == n_se.hint_resp_hash_salt

            # Update curr entry
            self._current_se = n_se

            # Update df and write to file
            self._add_to_df(self._current_se)
            self._write_to_file()
            return True
        else:
            return False
