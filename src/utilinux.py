#!/usr/bin/python3
# -*- coding: utf-8 -*-
import subprocess, os, socket


def validate_ip(addr):
    try:
        socket.inet_aton(addr)
        return True # legal
    except socket.error:
        return False # Not legal


def get_stdout(pi):
    result = pi.communicate()
    if len(result[0])>0:
        return result[0]
    else:
        return result[1] # some error has occured


def killall(process_name):
    counter = 0
    pid = is_process_running(process_name)
    while pid!=0:
        execute_shell('kill '+str(pid))
        pid = is_process_running(process_name)
        counter += 1
    return counter


def execute_shell(command, error=''):
    return execute(command, wait=True, shellexec=True, errorstring=error)


def execute_shell_root(command, sudo_pwd='', error=''):
    command = "echo "+str(sudo_pwd)+" | sudo -S "+command
    return execute(command, wait=True, shellexec=True, errorstring=error)


def execute(command='', wait=True, shellexec=False, errorstring='', ags=None):
    try:
        if (shellexec):
            p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            p = subprocess.Popen(args=ags)

        if wait:
            p.wait()
            result = get_stdout(p)
            return result
        else:
            return p
    except subprocess.CalledProcessError as e:
        print('Error occured : '+errorstring)
        return errorstring
    except Exception as ea:
        print('Exception occured : '+ea.message)
        return errorstring


def is_process_running(name):
    cmd = 'ps aux |grep '+name+' |grep -v grep'
    s = execute_shell(cmd)

    if len(s)==0:
        return 0
    else:
        t = s.split()
        return int(t[1])


def check_dependency(packet_name):
    if len(check_sysfile(packet_name))==0:
        print(packet_name+" executable not found. Make sure you have installed "+packet_name)
        return False
    return True


def check_sysfile(filename):
    if os.path.exists('/usr/sbin/'+filename):
        return '/usr/sbin/'+filename
    elif os.path.exists('/sbin/'+filename):
        return '/sbin/'+filename
    else:
        return ''


def get_sysctl(setting, sudo_pwd):
    result = execute_shell_root('sysctl '+setting, sudo_pwd).decode("utf-8")
    if '=' in result:
        return result.split('=')[1].lstrip()
    else:
        return result


def set_sysctl(setting, value, sudo_pwd):
    return execute_shell_root('sysctl -w '+setting+'='+value, sudo_pwd).decode("utf-8")


def interface_iw(name):
    response = execute_shell('iwconfig').decode("utf-8")

    lines = response.splitlines()
    for line in lines:
        if not line.startswith(' ') and len(line)>0:
            text = line.split(' ')[0]
            if line.startswith(name):
                return text
    return False


def interface_if(name):
    response = execute_shell('ifconfig').decode("utf-8")
    lines = response.splitlines()

    for line in lines:
        if not line.startswith(' ') and len(line)>0:
            text = line.split(' ')[0]
            if text.startswith(name):
                return text
    return False

def check_eth_connected(sudo_pwd):
    response = execute_shell_root("ethtool eth0 | grep detected:", sudo_pwd).decode("utf-8")
    if "yes" in response:
        return True
    return False