from PyVaultCrypto import PyVaultCrypto
import pytest
import pdb
import pickle

@pytest.fixture
def pvc_pwd():
    pwd = 'xyz123'
    cl = PyVaultCrypto(pwd)

    return cl, pwd

def test_pwd_hash(pvc_pwd):
    cl, pwd = pvc_pwd

    assert cl.verify_password(pwd) == True

    assert cl.verify_password(pwd + 'z') == False


def test_str_crypt(pvc_pwd):
    cl, pwd = pvc_pwd

    pt = 'India Russia US'
    ct, iv = cl.encrypt(pt)

    dt = cl.decrypt(ct)

    assert dt == pt

def test_obj_crypt(pvc_pwd):
    cl, pwd = pvc_pwd

    obj = ('India Russia US', [1, 2, 4])
    objs = pickle.dumps(obj)

    # pdb.set_trace()
    ct, iv = cl.encrypt(objs)

    dobjs = cl.decrypt(ct, returnAsBytes=True)
    dobj = pickle.loads(dobjs)

    assert dobj == obj