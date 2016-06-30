#!/usr/bin/python3
# -*- coding: utf-8 -*-
# sudo iw dev wlan0 station dump
# sudo arp
import utilinux as ut
import os


class Hotspot(object):
    def __init__(self, ssid="", password="", ip="", inet="", wlan="", netmask="255.255.255.0"):
        self.ssid = ssid
        self.password = password
        self.ip = ip
        self.inet = inet
        self.wlan = wlan
        self.netmask = netmask

        self.default_rundat = ['interface=wlan0\n', 'driver=nl80211\n', 'ssid=<SSID>\n', 'hw_mode=g\n', 'channel=6\n',
                               'macaddr_acl=0\n', 'ignore_broadcast_ssid=0\n', 'auth_algs=1\n', 'wpa=3\n',
                               'wpa_passphrase=<PASS>\n', 'wpa_key_mgmt=WPA-PSK\n', 'wpa_pairwise=TKIP\n',
                               'rsn_pairwise=CCMP\n']

    def check_sudo_password(self, sudo_pwd):
        response = ut.execute_shell("echo "+sudo_pwd+" | sudo -S whoami").decode("utf-8")

        if response.startswith('root'):
            print("[+] Root password is valid.")
            return True
        else:
            print("[!] Root password is not valid.")
            return False

    def check_interfaces(self):
        if not ut.interface_if(self.wlan):
            return "wlan"
        elif not ut.interface_if(self.inet):
            return "network"

        return "verified"

    def stop(self, sudo_pwd):
        # bring down the interface
        ut.execute_shell_root('ifconfig mon.'+self.wlan+' down', sudo_pwd)

        # Disable forwarding in iptables.
        ut.execute_shell_root('iptables -P FORWARD DROP', sudo_pwd)

        # delete iptables rules that were added for wlan traffic.
        if self.wlan!=None:
            ut.execute_shell_root('iptables -D OUTPUT --out-interface '+self.wlan+' -j ACCEPT', sudo_pwd)
            ut.execute_shell_root('iptables -D INPUT --in-interface '+self.wlan+' -j ACCEPT', sudo_pwd)
        ut.execute_shell_root('iptables --table nat --delete-chain', sudo_pwd)
        ut.execute_shell_root('iptables --table nat -F', sudo_pwd)
        ut.execute_shell_root('iptables --table nat -X', sudo_pwd)

        # disable forwarding in sysctl.
        ut.set_sysctl('net.ipv4.ip_forward', '0', sudo_pwd)

        ut.execute_shell_root('nmcli radio wifi on', sudo_pwd)
        ut.execute_shell_root('nmcli nm wifi on', sudo_pwd)

        return True

    def start(self, sudo_pwd):
        # stop
        ut.execute_shell_root('nmcli radio wifi off', sudo_pwd)
        ut.execute_shell_root('nmcli nm wifi off', sudo_pwd)
        ut.execute_shell_root('rfkill unblock wlan', sudo_pwd)
        ut.execute_shell_root('sleep 1', sudo_pwd)

        # create interface
        s = 'ifconfig '+self.wlan+' up '+self.ip+' netmask '+self.netmask
        ut.execute_shell_root(s, sudo_pwd)
        ut.execute_shell_root('sleep 2', sudo_pwd)
        i = self.ip.rindex('.')
        ipparts = self.ip[0:i]

        # stop hostapd if already running.
        if ut.is_process_running('hostapd')>0:
            ut.execute_shell_root('killall hostapd', sudo_pwd)

        if ut.is_process_running('dnsmasq')>0:
            ut.execute_shell_root('killall dnsmasq', sudo_pwd)

        ut.set_sysctl('net.ipv4.ip_forward', '1', sudo_pwd)
        ut.execute_shell_root('iptables -P FORWARD ACCEPT', sudo_pwd)

        # add iptables rules to create the NAT.
        ut.execute_shell_root('iptables --table nat --delete-chain', sudo_pwd)
        ut.execute_shell_root('iptables --table nat -F', sudo_pwd)
        ut.execute_shell_root('iptables --table nat -X', sudo_pwd)
        ut.execute_shell_root('iptables -t nat -A POSTROUTING -o '+self.inet+' -j MASQUERADE', sudo_pwd)
        ut.execute_shell_root(
                'iptables -A FORWARD -i '+self.inet+' -o '+self.wlan+' -j ACCEPT -m state --state RELATED,ESTABLISHED',
                sudo_pwd)
        ut.execute_shell_root('iptables -A FORWARD -i '+self.wlan+' -o '+self.inet+' -j ACCEPT', sudo_pwd)

        # allow traffic to/from wlan
        ut.execute_shell_root('iptables -A OUTPUT --out-interface '+self.wlan+' -j ACCEPT', sudo_pwd)
        ut.execute_shell_root('iptables -A INPUT --in-interface '+self.wlan+' -j ACCEPT', sudo_pwd)

        # start dnsmasq
        s = 'dnsmasq --dhcp-authoritative --interface='+self.wlan+' --dhcp-range='+ipparts+'.20,'+ipparts+'.100,'+self.netmask+',4h'
        ut.execute_shell_root(s, sudo_pwd)

        s = 'hostapd -B '+os.getcwd()+'/run.conf'
        ut.execute_shell('sleep 2')
        ut.execute_shell_root(s, sudo_pwd)

        print("[+] Hotspot is created.")
        return True

    def verify(self):
        # check dependencies
        if not ut.check_dependency("hostapd"):
            print("[!] hostapd couldn't be found. Try sudo apt-get install hostapd")
            return False

        if not ut.check_dependency("dnsmasq"):
            print("[!] dnsmasq couldn't be found.")
            return False
        print("[+] Depencencies are verified.")

        # verify connections
        if not ut.interface_iw(self.wlan):
            print("[!] Wireless interface could not be found.")
            return False

        if not ut.interface_if(self.inet):
            print("[!] Network inteface could not be found.")
            return False

        if not ut.validate_ip(self.ip):
            print("[!] IP is illegal.")
            self.ip = "192.168.99.1"
            print("[+] IP automatically setted to 192.168.99.1")

        if not os.path.isfile('./run.dat'):
            with open('run.dat', 'w') as fo:
                fo.writelines(self.default_rundat)

        lout = []
        with open('run.dat', 'r') as fo:
            for line in fo.readlines():
                lout.append(line.replace('<SSID>', self.ssid+"_Faunus").replace('<PASS>', self.password))

        with open('run.conf', 'w') as fo:
            fo.writelines(lout)

        print("[+] Created hostapd configuration : run.conf")
        return True

    def is_running(self):
        if (ut.is_process_running('hostapd')!=0):
            return True
        return False

    def check_eth_connected(self, sudo_pwd):
        return ut.check_eth_connected(sudo_pwd)
