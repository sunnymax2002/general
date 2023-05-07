import PySimpleGUI as sg

k_btn_se = 'btn_search_entry'
k_lbl_pe = 'lbl_parent_entry'
k_txt_se = 'txt_search_entry'
k_lbl_prompt = 'lbl_prompt'
k_lbl_hint = 'lbl_hint'
k_txt_pwd = 'txt_pwd'
k_btn_oe = 'btn_open_entry'

default_lbl_pe = "Parent Entry: None"
default_txt_se = "Enter the search text"
default_lbl_hint = "Password Hint"
default_lbl_prompt = ""

layout = [
    [
    sg.Text(default_lbl_pe, key=k_lbl_pe)
    ],
    [
    sg.In(default_txt_se, enable_events=True, key=k_txt_se),
    sg.Button("Search", key=k_btn_se)
    ],
    [
    sg.Text(default_lbl_hint, key=k_lbl_hint)
    ],
    [
    sg.In(enable_events=True, key=k_txt_pwd, password_char='*'),
    sg.Button("Open", key=k_btn_oe, disabled=True)
    ],
    [
    sg.Text(default_lbl_prompt, key=k_lbl_prompt)
    ]
    ]

window = sg.Window(title="Py Vault by Sunny", layout=layout, margins=(100, 50))

# Event Loop
while True:
    event, values = window.read()

    # End App
    if event == sg.WIN_CLOSED:
        break
    elif event == k_btn_se:
        search_txt = values[k_txt_se]
        pwd = values[k_txt_pwd]
        window[k_lbl_prompt].update("search: " + search_txt + " " + pwd)

window.close()