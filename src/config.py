#!/usr/bin/python3
# -*- coding: utf-8 -*-
import ast, os

KEY1 = "Key1"
KEY2 = "Key2"
KEY3 = "Key3"

DEFAULT_SETTINGS = {'loged_in':False,
                    'automail':True,
                    'startup_automail':True}
DEFAULT_DATA = {'username':"",
                'password':"",
                'imap_server':'imap.metu.edu.tr',
                'imap_port':'993',
                'smtp_server':'smtp.metu.edu.tr',
                'smtp_port':'587'}
settings = {} # settings
dirs = {} # important directories of project
data = {} # Username, password etc.


def init():
    global settings, dirs, data

    # Initialize dirs
    dirs["console"] = os.getcwd()
    dirs["src"] = os.path.dirname(__file__)
    dirs["project"] = os.path.abspath(os.path.join(dirs["src"], os.path.pardir))
    dirs["res"] = os.path.join(dirs["project"], "res")
    dirs["app_icon"] = os.path.join(dirs["res"], "app_icon.png")
    dirs["tray_icon"] = os.path.join(dirs["res"], "tray_icon.png")
    dirs["mail_icon"] = os.path.join(dirs["res"], "mail_icon.png")
    dirs["config"] = os.path.join(dirs["src"], "config.dict")
    dirs["data"] = os.path.join(dirs["src"], "data.dict")

    # Initialize settings
    if os.path.isfile(dirs["config"]):
        with open(dirs["config"], "r") as fo:
            response = fo.read()

        try:
            settings = ast.literal_eval(response)
        except:
            print("[!] Config file is not valid. Loading default settings.")
            set_default_settings()
    else:
        print("[!] There is no config file. I am creating one for you :)")
        set_default_settings()

    # Initialize data
    if os.path.isfile(dirs["data"]):
        with open(dirs["data"], "r") as fo:
            response = fo.read()

        try:
            data = ast.literal_eval(response)
        except:
            print("[!}] Data file is not valid. Creating fresh data.")
            set_default_data()
    else:
        print("[!] There is no data file. I am creating one for you :)")
        set_default_data()


def set_default_data():
    global data
    data = DEFAULT_DATA.copy()
    with open(dirs["data"], "w") as fo:
        fo.write(str(data))


def set_default_settings():
    global settings
    settings = DEFAULT_SETTINGS.copy()
    with open(dirs["config"], "w") as fo:
        fo.write(str(settings))


def save_data():
    with open(dirs["data"], "w") as fo:
        fo.write(str(data))


def save_settings():
    with open(dirs["config"], "w") as fo:
        fo.write(str(settings))


def set_encrypted_data(item, value):
    value = enc(value)
    data[item] = value


def get_encypted_data(item):
    value = data[item]
    print(value)
    value = "".join(map(chr, value))
    value = enc(value)
    value = "".join(map(chr, value))
    return value


def enc(s, k=KEY1):
    k = k*(int(len(s)/len(k))+1)
    return [ord(s[i]) ^ ord(k[i]) for i in range(len(s))]


init()
