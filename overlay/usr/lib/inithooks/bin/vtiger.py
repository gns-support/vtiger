#!/usr/bin/python
"""Set Vtiger admin password and email

Option:
    --pass=     unless provided, will ask interactively
    --email=    unless provided, will ask interactively

"""

import sys
import getopt
import hashlib
from os.path import *
import subprocess
from subprocess import PIPE

from dialog_wrapper import Dialog
from mysqlconf import MySQL

def fatal(s):
    print >> sys.stderr, "Error:", s
    sys.exit(1)

def usage(s=None):
    if s:
        print >> sys.stderr, "Error:", s
    print >> sys.stderr, "Syntax: %s [options]" % sys.argv[0]
    print >> sys.stderr, __doc__
    sys.exit(1)

def main():
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "h",
                                       ['help', 'pass=', 'email='])
    except getopt.GetoptError, e:
        usage(e)

    password = ""
    email = ""
    for opt, val in opts:
        if opt in ('-h', '--help'):
            usage()
        elif opt == '--pass':
            password = val
        elif opt == '--email':
            email = val

    if not email:
        d = Dialog('TurnKey Linux - First boot configuration')

        email = d.get_email(
            "Vtiger Email",
            "Enter email address for the Vtiger 'admin' account.",
            "admin@example.com")

    if not password:
        if 'd' not in locals():
            d = Dialog('TurnKey Linux - First boot configuration')

        password = d.get_password(
            "Vtiger Password",
            "Enter new password for the Vtiger 'admin' account.")


    hashpass = hashlib.md5(password).hexdigest()

    command = ["php", join(dirname(__file__), 'vt_crypt.php'), "admin", password]
    p = subprocess.Popen(command, stdin=PIPE, stdout=PIPE, shell=False)
    stdout, stderr = p.communicate()
    if stderr:
        fatal(stderr)

    cryptpass = stdout.strip()

    m = MySQL()
    m.execute('UPDATE vtigercrm.vtiger_users SET email1=\"%s\" WHERE user_name=\"admin\";' % email)
    m.execute('UPDATE vtigercrm.vtiger_users SET user_hash=\"%s\" WHERE user_name=\"admin\";' % hashpass)
    m.execute('UPDATE vtigercrm.vtiger_users SET user_password=\"%s\" WHERE user_name=\"admin\";' % cryptpass)


if __name__ == "__main__":
    main()

