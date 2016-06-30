#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys, mail, view
from config import * # includes : conf, dirs, encrypt, decrypt, save_conf
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import *

tmp["platform"] = sys.platform

if tmp["platform"]=="linux" or tmp["platform"]=="linux2":
    from hotspotlinux import Hotspot
    tmp['platform'] = 'linux'
#else
#    from hotspotwindows import Hotspot
#    tmp['platform'] = 'win32'

class Faunus(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = view.Ui_Faunus()
        self.ui.setupUi(self)
        self.init_faunus()

    def init_faunus(self):
        if tmp['platform']=='linux':
            self.ui.tabWidget_main.removeTab(3)
        else:
            self.ui.tabWidget_main.removeTab(2)

        # mail
        self.ui.chb_automail.stateChanged.connect(self.handle_automail)
        self.ui.chb_startup_automail.stateChanged.connect(self.handle_startup_automail)
        self.ui.btn_mail_save.clicked.connect(self.mail_save)
        self.ui.btn_mail_reset.clicked.connect(self.mail_reset)

        if conf['faunus']['num_of_mailbox']:
            self.ui.lne_imap_server.setText(conf["mailbox0"]["imap_server"])
            self.ui.lne_imap_port.setText(conf["mailbox0"]["imap_port"])
            self.ui.lne_smtp_server.setText(conf["mailbox0"]["smtp_server"])
            self.ui.lne_smtp_port.setText(conf["mailbox0"]["smtp_port"])
            self.ui.lne_username.setText(conf["mailbox0"]["username"])
            self.ui.lne_password.setText("password")
            self.init_mail()
        else:
            self.ui.btn_mail_reset.setDisabled(True)
            self.ui.chb_automail.setDisabled(True)

        # hotspot
        self.ui.btn_hotspot_on.clicked.connect(self.hotspot_on)
        self.ui.btn_hotspot_off.clicked.connect(self.hotspot_off)
        self.ui.btn_hotspot_save.clicked.connect(self.hotspot_save)
        self.ui.btn_hotspot_reset.clicked.connect(self.hotspot_reset)

        if conf['hotspot']['saved']:
            self.ui.lne_hotspot_name.setText(conf['hotspot']['ssid'])
            self.ui.lne_hotspot_password.setText(conf['hotspot']['password'])
            self.ui.lne_hotspot_wlan.setText(conf['hotspot']['wlan'])
            self.ui.lne_hotspot_inet.setText(conf['hotspot']['inet'])
            self.ui.lne_sudo_password.setText("password")
            self.init_hotspot()
        else:
            self.ui.btn_hotspot_on.setDisabled(True)
            self.ui.btn_hotspot_off.setDisabled(True)

    # hotspot part
    def init_hotspot(self):
        self.ui.btn_hotspot_on.setDisabled(False)
        self.ui.btn_hotspot_off.setDisabled(False)
        self.hotspot = Hotspot()
        self.load_hotspot_settings(self.hotspot)

        if conf['hotspot']['startup']:
            self.ui.chb_startup_hotspot.setChecked(True)
            self.ui.btn_hotspot_on.click()

        self.hotspot_disabled(True)

    def hotspot_disabled(self, state):
        self.ui.lne_hotspot_inet.setReadOnly(state)
        self.ui.lne_hotspot_wlan.setReadOnly(state)
        self.ui.groupBox_hotspot_settings.setDisabled(state)

    def hotspot_on(self):
        response = self.hotspot.check_interfaces()
        if response=="verified" and self.hotspot.check_eth_connected( decrypt(conf['faunus']['sudo_pwd']) ):
            print( self.hotspot.start(decrypt(conf['faunus']['sudo_pwd'])))

            self.ui.lbl_hotspot_status.setText("ON")
            print("[+] Hotspot is turned on")
            self.ui.statusBar.showMessage("Hotspot is ON", 2000)
        else:
            print("[!] wlan or network interface was not found. Make sure your wifi is on and connected to internet.")
            self.ui.statusBar.showMessage("UNSUCCESSFUL connect internet, turn on wifi", 5000)

    def hotspot_off(self):
        self.hotspot.stop(decrypt(conf['faunus']['sudo_pwd']))
        self.ui.lbl_hotspot_status.setText("OFF")
        print("[-] Hotspot is turned off")
        self.ui.statusBar.showMessage("Hotspot is OFF", 2000)

    def hotspot_save(self):
        hs = Hotspot()
        if not conf["faunus"]["sudo_pwd"]:
            sudo_pwd = self.ui.lne_sudo_password.text()

            if hs.check_sudo_password(sudo_pwd):
                conf["faunus"]["sudo_pwd"] = encrypt(sudo_pwd)
                save_conf()
                self.ui.statusBar.showMessage("SUDO password is SAVED", 2000)
            else:
                self.ui.statusBar.showMessage("SUDO password is WRONG", 2000)
                print("[!] Wrong sudo password. Didn't saved")
                return

        ssid = self.ui.lne_hotspot_name.text().strip()
        if ssid=="":
            QMessageBox.warning(self, "Fill the Gaps", "Hotspot name is empty. Try again.", QMessageBox.Close)
            return

        pwd = self.ui.lne_hotspot_password.text().strip()
        if len(pwd)<10:
            QMessageBox.warning(self, "Fill the Gaps", "Password should be more than 10 character. Try again.",
                                QMessageBox.Close)
            return

        inet = self.ui.lne_hotspot_inet.text().strip()
        if not inet: inet = "eth0"

        wlan = self.ui.lne_hotspot_wlan.text().strip()
        if not wlan: wlan = "wlan0"

        self.load_hotspot_settings(hs, ssid, pwd, inet, wlan, "192.168.99.1", "255.255.255.0")

        if hs.verify():
            self.ui.statusBar.showMessage("Hotspot is SAVED", 2000)
            conf['hotspot']['saved'] = True
            conf['hotspot']['ssid'] = ssid
            conf['hotspot']['password'] = pwd
            conf['hotspot']['wlan'] = wlan
            conf['hotspot']['inet'] = inet
            conf['hotspot']['ip'] = "192.168.99.1"
            conf['hotspot']['netmask'] = "255.255.255.0"
            save_conf()
            self.init_hotspot()

    def load_hotspot_settings(self, hs, ssid="", pwd="", inet="", wlan="", ip="", netmask=""):
        if ssid:
            hs.ssid = ssid
            hs.password = pwd
            hs.inet = inet
            hs.wlan = wlan
            hs.ip = ip
            hs.netmask = netmask
        else:
            hs.ssid = conf['hotspot']['ssid']
            hs.password = conf['hotspot']['password']
            hs.inet = conf['hotspot']['inet']
            hs.wlan = conf['hotspot']['wlan']
            hs.ip = conf['hotspot']['ip']
            hs.netmask = conf['hotspot']['netmask']

    def hotspot_reset(self):
        pass

    # mail part
    def init_mail(self):
        self.mailbox = mail.MailBox()

        self.load_mailbox_settings(self.mailbox, "mailbox0")

        self.automail_thread = MailThread(self.mailbox)
        self.automail_thread.mailsignal.connect(self.handle_new_mail)

        self.automail_timer = QTimer()
        self.automail_freq = 5000 # check mail once in X second
        self.automail_timer.timeout.connect(self.automail_thread.start)

        self.ui.chb_automail.setDisabled(False)

        if conf["mailbox0"]["startup"]:
            self.ui.chb_startup_automail.setChecked(True)
            self.ui.chb_automail.setChecked(True)

        self.mail_disabled(True)

    def mail_disabled(self, state):
        self.ui.groupBox_mail_account.setDisabled(state)
        self.ui.groupBox_mail_imap.setDisabled(state)
        self.ui.groupBox_mail_smtp.setDisabled(state)
        self.ui.btn_mail_save.setDisabled(state)
        self.ui.btn_mail_reset.setDisabled(not state)

    # will be notification here
    def handle_new_mail(self, new_mail):
        self.ui.statusBar.showMessage("You have "+str(new_mail)+" unseen messages", 2000)

    def load_mailbox_settings(self, mailbox, mailbox_id="", uname="", pwd="", imapsw="", imapprt="", smtpsw="",
                              smtpprt=""):
        if mailbox_id:
            mailbox.username = conf[mailbox_id]["username"]
            mailbox.password = decrypt(conf[mailbox_id]["password"])
            mailbox.imap_server = conf[mailbox_id]["imap_server"]
            mailbox.imap_port = conf[mailbox_id]["imap_port"]
            mailbox.smtp_server = conf[mailbox_id]["smtp_server"]
            mailbox.smtp_port = conf[mailbox_id]["smtp_port"]
        else:
            mailbox.username = uname
            mailbox.password = pwd
            mailbox.imap_server = imapsw
            mailbox.imap_port = imapprt
            mailbox.smtp_server = smtpsw
            mailbox.smtp_port = smtpprt

    def mail_save(self):
        tmp_mailbox = mail.MailBox()
        tmp_username = self.ui.lne_username.text()
        tmp_password = self.ui.lne_password.text()
        tmp_imap_server = self.ui.lne_imap_server.text()
        tmp_imap_port = self.ui.lne_imap_port.text()
        tmp_smtp_server = self.ui.lne_smtp_server.text()
        tmp_smtp_port = self.ui.lne_smtp_port.text()
        self.load_mailbox_settings(tmp_mailbox, '', tmp_username, tmp_password, tmp_imap_server, tmp_imap_port,
                                   tmp_smtp_server, tmp_smtp_port)
        response = tmp_mailbox.check_imap_response()

        if response!="valid":
            QMessageBox.warning(self, "Connection Error", response+" is not valid. Please check your informations.",
                                QMessageBox.Close)
            print("[!] "+response+" is not valid. Not saved")
            return

        mailbox_id = 'mailbox'+str(conf["faunus"]["num_of_mailbox"])
        conf[mailbox_id] = {}
        conf[mailbox_id]["username"] = tmp_username
        conf[mailbox_id]["password"] = encrypt(tmp_password)
        conf[mailbox_id]["imap_server"] = tmp_imap_server
        conf[mailbox_id]["imap_port"] = tmp_imap_port
        conf[mailbox_id]["smtp_server"] = tmp_smtp_server
        conf[mailbox_id]["smtp_port"] = tmp_smtp_port
        conf[mailbox_id]["startup"] = bool(self.ui.chb_startup_automail.checkState())
        conf["faunus"]["num_of_mailbox"] += 1
        save_conf()

        self.ui.statusBar.showMessage("Accound is SAVED", 3000)
        print("[+] Account is SAVED")

        self.init_mail()

    def mail_reset(self):
        print( "---------",self.ui.lne_hotspot_name.text() )

    def handle_automail(self, state):
        if state:
            self.automail_timer.start(self.automail_freq)
            self.ui.statusBar.showMessage("Automail checking is ENABLED", 1500)
            print("[+] Automail checking is ENABLED")
        else:
            self.automail_timer.stop()
            self.ui.statusBar.showMessage("Automail checking is DISABLED", 1500)
            print("[-] Automail checking is DISABLED")

    def handle_startup_automail(self, state):
        conf["mailbox0"]["startup"] = bool(state)
        state = "ENABLED" if state else "DISABLED"
        self.ui.statusBar.showMessage("Startup is "+state, 1500)
        print("[+] Startup is "+state)

        save_conf()


class MailThread(QThread):
    mailsignal = pyqtSignal(int)

    def __init__(self, mailbox):
        QThread.__init__(self)

        self.mailbox = mailbox

    def run(self):
        self.check_mail()

    def check_mail(self):
        new_mail = self.mailbox.check_new_mail()
        self.mailsignal.emit(new_mail)


if __name__=="__main__":
    app = QApplication(sys.argv)
    myapp = Faunus()
    myapp.setWindowIcon(QIcon(dirs["app_icon"]))
    myapp.show()
    sys.exit(app.exec_())
