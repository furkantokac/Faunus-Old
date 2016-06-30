# #!/usr/bin/python3
# -*- coding: UTF-8 -*-
import socket, imaplib, smtplib


class MailBox(object):
    def __init__(self, uname="", passwd="", imapsw="", imapprt="", smtpsw="", smtpprt=""):
        self.username = uname
        self.password = passwd
        self.imap_server = imapsw
        self.imap_port = imapprt
        self.smtp_server = smtpsw
        self.smtp_port = smtpprt

    # IMAP
    def check_new_mail(self):
        try:
            server = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            server.login(self.username, self.password)
        except:
            print("[!] Cannot connect imap server. Probably poor internet connection problem.")
            return -1

        server.select('INBOX')
        # server.search(None, 'unseen') returns ('OK', [b'818 819']) so
        new_mail = server.search(None, 'unseen')[1][0]
        new_mail = new_mail.decode("utf-8")

        # close & logout
        server.close()
        server.logout()

        # Means no new mail
        if len(new_mail)==0:
            return 0

        new_mail = new_mail.split(' ')
        return len(new_mail)

    def check_imap_response(self):
        socket.setdefaulttimeout(2)
        try:
            server = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
        except:
            socket.setdefaulttimeout(5)
            return "Server"
        try:
            server.login(self.username, self.password)
        except:
            socket.setdefaulttimeout(5)
            return "Username/Password"

        socket.setdefaulttimeout(5)
        return "valid"

    # SMTP
    def check_smtp_response(self):
        socket.setdefaulttimeout(2)
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
        except:
            socket.setdefaulttimeout(5)
            return "Server"
        try:
            server.login(self.username, self.password)
        except:
            socket.setdefaulttimeout(5)
            return "Username/Password"

        socket.setdefaulttimeout(5)
        return "valid"
