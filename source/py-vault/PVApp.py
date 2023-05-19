import PySimpleGUI as sg
from PyVault import PyVault
from SecureEntry import SecureEntry as se
from os import path

import sys
if not sys.version_info >= (3, 6):
   print("This program uses Python 3.6 features, please upgrade your Python version")

# REF: https://realpython.com/pysimplegui-python/

k_txt_mpwd = 'txt_mpwd'
k_btn_unlock = 'btn_unlock'

# k_lbl_pe = 'lbl_parent_entry'
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

k_lst_setree = 'lst_setree'

# Dictionary of name:id to get to an entry in parent treee
se_tree_dict = {}

layout = [
    [
    sg.Text('Enter Master Password', key='lbl_mpwd'),
    sg.In(enable_events=True, key=k_txt_mpwd, password_char='*'),
    sg.Button("Unlock", key=k_btn_unlock)
    ],
    [
    sg.Listbox(list(se_tree_dict.keys()), size=(20, 4), expand_y=True, enable_events=True, key=k_lst_setree, disabled=True, select_mode='single')
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
    pv.add_entry(n, h, hr, d, setAsCurrent=True)


def get_parent() -> str:
    return pv.get_entry_tree()


def update_curr_selected(n: str, h: str):
    pass

def update_se_tree():
    global se_tree_dict

    se_tree_dict = pv.get_entry_tree()
    window[k_lst_setree].update(disabled=False, values=list(se_tree_dict.keys()), set_to_index=len(se_tree_dict.keys())-1)

def clear_fields():
    window[k_txt_se].update(values=[])
    window[k_txt_hint].update(value='')
    window[k_txt_pwd].update(value='')
    window[k_txt_sdata].update(value='')

def open_entry(id: int):
    # Open n/h w/o pwd
    pv.open_entry(id, setAsCurrent=True)

    # Fetch name and hint and populate
    n, h = pv.get_name_hint_by_id(id)

    clear_fields()
    window[k_txt_se].update(values=[n], set_to_index=0)
    window[k_txt_hint].update(value=h)

    # Enable Open button
    window[k_btn_oe].update(disabled=False)

def close_all():
    pv.close_all()
    clear_fields()
    window[k_btn_oe].update(disabled=True)

def get_selected_id():
    sel = values[k_lst_setree][0]
    # Get id of selected entry in the tree
    return se_tree_dict[sel]

# Event Loop
while True:
    event, values = window.read()

    # End App
    if event == sg.WIN_CLOSED:
        break

    elif event == k_btn_unlock:
        window[k_btn_unlock].set_cursor("clock")
        try:
            # Unlock using Master Password
            pv = read_pv_data(values[k_txt_mpwd])
        except Exception as e:
            sg.popup_error('Incorrect Master Password')
            # window[k_lbl_prompt].update('Incorrect Master Password')
        else:
            # Unlock other GUI elements, if unlocked successfully
            update_se_tree()
            window[k_txt_se].update(disabled=False)
            window[k_btn_se].update(disabled=False)
            window[k_txt_hint].update(disabled=False)
            window[k_txt_pwd].update(disabled=False)
            window[k_txt_sdata].update(disabled=False)
            window[k_btn_sdata].update(disabled=False)
        finally:
            window[k_btn_unlock].set_cursor("arrow")

    elif event == k_btn_se:
        # Search for Entry
        search_txt = values[k_txt_se]

        # If root, or current entry unlocked, then only search
        if pv.is_curr_entry_unlocked():
            entries = search_entry(search_txt)

            # window[k_lbl_prompt].update('{0} matching entries found'.format(len(entries)))
            if len(entries) > 0:
                window[k_txt_se].update(values=list(entries.keys()), set_to_index=0)

                if len(entries) == 1:
                    id = list(entries.values())[0]
                    open_entry(id)
                
                update_se_tree()
            else:
                sg.popup_error('No maching entry found')
        else:
            sg.popup_error('Before searching, Open the selected entry first by providing Hint Response')
    
    elif event == k_btn_sdata:
        # If root, or current entry unlocked, then only add
        if pv.is_curr_entry_unlocked():
            n = values[k_txt_se]
            h = values[k_txt_hint]
            hr = values[k_txt_pwd]
            d = values[k_txt_sdata]

            msg = 'Name={0}\nHint={1}\nHint Respose={2}\nData={3}'.format(n, h, hr, d)
            ch = sg.popup_ok_cancel(msg, '',  title="Confirm Entry Addition")

            if ch == 'OK':
                add_entry(n, h, hr, d)
                update_se_tree()
        else:
            sg.popup_error('Before Adding, Open the selected entry first by providing Hint Response')

    elif event == k_lst_setree:
        id = get_selected_id()
        if id is None:
            close_all()
        else:
            open_entry(id)
        
        update_se_tree()
    
    elif event == k_btn_oe:
        id = get_selected_id()
        hr = values[k_txt_pwd]

        window[k_btn_oe].set_cursor("clock")
        sc = pv.get_entry_securecontent(id, hr)
        window[k_btn_oe].set_cursor("arrow")

        if sc is None:
            sg.popup_error('Incorrect Hint Response')
        else:
            window[k_txt_sdata].update(value=sc)
            # TODO: add timeout to clear k_txt_sdata

window.close()