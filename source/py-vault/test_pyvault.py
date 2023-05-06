from PyVaultCrypto import PyVaultCrypto
# from PyVault import PyVault
from SecureEntry import SecureEntry
import pytest
import pdb
import pickle
import pandas as pd

@pytest.fixture
def pvc_pwd():
    pwd = 'xyz123'
    cl = PyVaultCrypto(pwd)

    return cl, pwd

def _t_pwd_hash(cl, pwd):
    assert cl.verify_password(pwd) == True
    assert cl.verify_password(pwd + 'z') == False


def _t_str_crypt(cl, pwd):
    pt = 'India Russia US'
    ct, iv = cl.encrypt(pt)
    dt = cl.decrypt(ct)
    assert dt == pt


def _t_obj_crypt(cl, pwd):
    obj = ('India Russia US', [1, 2, 4])
    objs = pickle.dumps(obj)
    ct, iv = cl.encrypt(objs)
    dobjs = cl.decrypt(ct, returnAsBytes=True)
    dobj = pickle.loads(dobjs)
    assert dobj == obj


def test_pwd_hash(pvc_pwd):
    cl, pwd = pvc_pwd
    _t_pwd_hash(cl, pwd)


def test_str_crypt(pvc_pwd):
    cl, pwd = pvc_pwd
    _t_str_crypt(cl, pwd)


def test_obj_crypt(pvc_pwd):
    cl, pwd = pvc_pwd
    _t_obj_crypt(cl, pwd)


def test_persistent_data_pvc(pvc_pwd):
    cl, pwd = pvc_pwd
    pd_cl = PyVaultCrypto.from_persistent_data(cl.hash, cl.salt, cl.iv, pwd)
    _t_pwd_hash(pd_cl, pwd)
    _t_str_crypt(pd_cl, pwd)
    _t_obj_crypt(pd_cl, pwd)


###########################

def test_new_secure_entry(pvc_pwd):
    mpvc, pwd = pvc_pwd
    cust_id = '123'
    cid_secret = 'secret'
    e1_n = 'hdfc'
    e1_h = 'cust-id'
    e1 = SecureEntry.from_new_data(1, None, e1_n, e1_h, cust_id, cid_secret, mpvc)

    dc_4dig = '9876'
    dc_pin = 'pin'
    e2_n = 'debit card'
    e2_h = 'Last 4 digits of card'
    e2 = SecureEntry.from_new_data(2, 1, e2_n, e2_h, dc_4dig, dc_pin, e1.get_pvc())

    cc_4dig = '5678'
    cc_pin = 'pin2'
    e3_n = 'credit card'
    e3_h = 'Last 4 digits of card'
    e3 = SecureEntry.from_new_data(3, 1, e3_n, e3_h, cc_4dig, cc_pin, e1.get_pvc())

    e1.add_child(e2)
    e1.add_child(e3)

    name, hint, data, child_dict = e1.get_content()
    assert name == e1_n
    assert hint == e1_h
    assert data == cid_secret
    assert list(child_dict.keys()) == [e2_n, e3_n]

    name, hint, data, child_dict = e2.get_content()
    assert name == e2_n
    assert hint == e2_h
    assert data == dc_pin
    assert len(child_dict) == 0

    name, hint, data, child_dict = e3.get_content()
    assert name == e3_n
    assert hint == e3_h
    assert data == cc_pin
    assert len(child_dict) == 0

    entries = [e1.get_persistent_data(), e2.get_persistent_data(), e3.get_persistent_data()]

    df = pd.DataFrame.from_dict(entries).set_index('id')

    # TODO: add checker for df/get_persistent_data
    print(df)