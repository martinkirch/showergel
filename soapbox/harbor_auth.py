#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script can back a custom authentication for ``input.harbor``,
where each user has her own password.
User names and passwords are stored in a file,
so accesses can be granted or revoked without rebooting Liquidsoap.
This script encrypts passwords before writing them to the users list.

Call it from Liquidsoap as follows::

    def auth_function(user,password) = 
        ret = get_process_output("/path/to/harbor_auth.py #{user} #{password}")
        if string.trim(ret) == "ok" then
            true
        else
            false
        end
    end

    harbor = input.harbor(auth=auth_function, ...

Before use, please edit the ``PASSWDFILE`` constant below.
Note that if something goes wrong during Liqudisoap's call,
this script write to syslog so you can still read error messages.

To add/update a user's password, invoke ``./harbor_auth.py --set USER PASSWORD``.
Later on, you can edit `PASSWDFILE`` to revoke an user's access:
just remove the line starting with the user's name.

This script can be copied and used outside soapbox.
"""

import os, sys, crypt, traceback
from hmac import compare_digest
import syslog

PASSWDFILE = "/home/radio/liquidsoap/harbor_auth.txt"

def load():
    try:
        with open(PASSWDFILE) as file:
            lines = file.readlines()
    except IOError:
        # log this, if it happesn in check()
        syslog.syslog(syslog.LOG_ERR,
            "Can't open %s, please check PASSWDFILE in harbor_auth.py" %
            PASSWDFILE
        )
        file = open(PASSWDFILE, "w")
        file.close()
        os.chmod(PASSWDFILE, 0o600)
        lines = []
    users = {}
    for line in lines:
        columns = line.strip().split("\t")
        if len(columns) == 2:
            users[columns[0]] = columns[1]
    return users

def check(user, mdp):
    try:
        existing = load()
        if user not in existing:
            print("nope")
        elif compare_digest(crypt.crypt(mdp, existing[user]), existing[user]):
            print("ok")
        else:
            print("nope")
    except:
        syslog.syslog(syslog.LOG_ERR, "Exception caught in harbor_auth.py's check():")
        syslog.syslog(syslog.LOG_ERR, traceback.format_exc())

def save(user, mdp):
    existing = load()
    existing[user] = crypt.crypt(mdp)
    with open(PASSWDFILE, 'w') as file:
        for util in existing:
            file.write(util)
            file.write("\t")
            file.write(existing[util])
            file.write("\n")


def main(argv):
    if len(argv) == 1:
        print(__doc__)
    elif len(argv) == 4 and argv[1] == "--set":
        save(argv[2], argv[3])
    elif len(argv) == 3:
        check(argv[1], argv[2])

if __name__ == '__main__':
    main(sys.argv)
