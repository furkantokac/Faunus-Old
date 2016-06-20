# #!/usr/bin/python3
# -*- coding: UTF-8 -*-
import imaplib, socket


class MailBox():
    def __init__(self):
        self.imap_server = ""
        self.imap_port = 0
        self.username = ""
        self.password = ""

    def check_new_mail(self):
        server = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
        server.login(self.username, self.password)
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

    def check_server_response(self):
        try:
            server = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
        except:
            return "Server"
        try:
            server.login(self.username, self.password)
        except:
            return "Username/Password"
        socket.setdefaulttimeout(5)
        return "valid"
