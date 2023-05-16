import PySimpleGUI as sg
from PyVault import PyVault
from SecureEntry import SecureEntry as se
from os import path

# REF: https://realpython.com/pysimplegui-python/

k_txt_mpwd = 'txt_mpwd'
k_btn_unlock = 'btn_unlock'

k_lbl_pe = 'lbl_parent_entry'
k_lbl_se = 'lbl_search_entry'
k_btn_se = 'btn_search_entry'
k_txt_se = 'txt_search_entry'

k_lbl_prompt = 'lbl_prompt'

k_lbl_hint = 'lbl_hint'
k_lbl_hintresp = 'lbl_hintresp'
k_txt_hint = 'txt_hint'

k_txt_pwd = 'txt_pwd'
k_btn_oe = 'btn_open_entry'

default_lbl_pe = "Parent Entry: Root"
default_lbl_se = "Seacrh Entry"

# Search Box / Drop-down
default_txt_se = "Entry Name / search text"
se_lst = [default_txt_se]

default_lbl_hint = "Hint"
default_lbl_hintresp = "Hint Response"
default_lbl_prompt = ""

k_lbl_sdata = 'lbl_sdata'
default_lbl_sdata = 'Secure Data'
default_txt_sdata = 'Enter Data to Secure'
k_txt_sdata = 'txt_sdata'
k_btn_sdata = 'btn_sdata'

layout = [
    [
    sg.Text('Enter Master Password', key='lbl_mpwd'),
    sg.In(enable_events=True, key=k_txt_mpwd, password_char='*'),
    sg.Button("Unlock", key=k_btn_unlock)
    ],
    [
    sg.Text(default_lbl_pe, key=k_lbl_pe)
    ],
    [
    sg.Text(default_lbl_se, key=k_lbl_se),
    sg.Combo(se_lst, default_value=default_txt_se, enable_events=True, key=k_txt_se, disabled=True),
    sg.Button("Search", key=k_btn_se, disabled=True)
    ],
    [
    sg.Text(default_lbl_hint, key=k_lbl_hint),
    sg.In(enable_events=True, key=k_txt_hint, disabled=True),
    ],
    [
    sg.Text(default_lbl_hintresp, key=k_lbl_hintresp),
    sg.In(enable_events=True, key=k_txt_pwd, password_char='*', disabled=True),
    sg.Button("Open", key=k_btn_oe, disabled=True)
    ],
    [
    sg.Text(default_lbl_sdata, key=k_lbl_sdata),
    sg.In(enable_events=True, key=k_txt_sdata, disabled=True, default_text=default_txt_sdata),
    sg.Button("Add", key=k_btn_sdata, disabled=True)
    ],
    [
    sg.Text(default_lbl_prompt, key=k_lbl_prompt)
    ]
    ]

window = sg.Window(title="Py Vault by Sunny", layout=layout, margins=(100, 50))

# View - Model interactions
pv = None

def read_pv_data(mpwd: str) -> PyVault:
    pkl_fpath=r"C:\Users\sunny\My Drive (sbav2309@gmail.com)\Home and Life\Vault\pvc_data.pkl"

    if path.exists(pkl_fpath):
        pv = PyVault.from_persistent_data(pkl_fpath, mpwd)
    else:
        pv = PyVault.from_new_data(mpwd, pkl_fpath)
    
    return pv


def search_entry(search_txt: str) -> dict:
    return pv.find_entry(search_txt)


def add_entry(n, h, hr, d):
    pv.add_entry(n, h, hr, d)


def get_parent() -> str:
    return pv.get_entry_tree()

# Event Loop
while True:
    event, values = window.read()

    # End App
    if event == sg.WIN_CLOSED:
        break

    elif event == k_btn_unlock:
        try:
            # Unlock using Master Password
            pv = read_pv_data(values[k_txt_mpwd])
        except Exception as e:
            ch = sg.popup_error('Incorrect Master Password')
            # window[k_lbl_prompt].update('Incorrect Master Password')
        else:
            # Unlock other GUI elements, if unlocked successfully
            window[k_txt_se].update(disabled=False)
            window[k_btn_se].update(disabled=False)
            window[k_txt_hint].update(disabled=False)
            window[k_txt_pwd].update(disabled=False)
            window[k_txt_sdata].update(disabled=False)
            window[k_btn_sdata].update(disabled=False)

    elif event == k_btn_se:
        # Search for Entry
        search_txt = values[k_txt_se]
        entries = search_entry(search_txt)

        # entries = {'hdfc': 1, 'zhdfc': 2}

        window[k_lbl_prompt].update('{0} matching entries found'.format(len(entries)))
        if len(entries) > 0:
            window[k_txt_se].update(values=list(entries.keys()), set_to_index=0)
    
    elif event == k_btn_sdata:
        n = values[k_txt_se]
        h = values[k_txt_hint]
        hr = values[k_txt_pwd]
        d = values[k_txt_sdata]

        msg = 'Name={0}\nHint={1}\nHint Respose={2}\nData={3}'.format(n, h, hr, d)
        ch = sg.popup_ok_cancel(msg, '',  title="Confirm Entry Addition")

        if ch == 'OK':
            add_entry(n, h, hr, d)
            
            # Update Parent Entry?
            window[k_lbl_pe].update(get_parent())

window.close()