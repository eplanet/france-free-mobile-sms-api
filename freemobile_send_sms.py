#!/usr/bin/python3

import argparse
import configparser
import getpass
import urllib.parse
import urllib.request
import os
import pwd
import sys

# Le code de retour HTTP indique le succès ou non de l'opération :
return_keys = { 200: "Le SMS a été envoyé sur votre mobile.",
               400: "Un des paramètres obligatoires est manquant.",
               402: "Trop de SMS ont été envoyés en trop peu de temps.",
               403: "Le service n'est pas activé sur l'Espace Abonné, ou login / clé incorrect.",
               500: "Erreur côté serveur. Veuillez réessayer ultérieurement." }


def change_user(user):
    try:
        newuid = pwd.getpwnam(user).pw_uid
        os.setuid(newuid)
        #if user is found change environ to later resolve its home
        pwdentry = pwd.getpwuid(os.geteuid())
        os.environ['HOME'] = pwdentry.pw_dir
        os.environ['LOGNAME'] = pwdentry.pw_name
    except KeyError as e:
        sys.exit(f'User {args.user} not found on the system')

def read_config():
    config = configparser.ConfigParser()
    configfile = os.path.expanduser('~/.freemobileconfig')
    if not os.path.isfile(configfile):
        sys.exit(f'No config file found in {getpass.getuser()} home')
    config.read(configfile)
    if not (config.has_option('id', 'user') and config.has_option('id', 'key')):
        sys.exit('Invalid config file')
    return config['id']['user'], config['id']['key']

def send_sms(msg, user=None):
    if user is not None:
        change_user(user)
    userid, key = read_config()
    f = { 'user' : userid, 'pass' : key, 'msg' : msg}
    url = "https://smsapi.free-mobile.fr/sendmsg?"
    # on encode le tout et on crée l'url d'envoi
    goto = url + urllib.parse.urlencode(f)
    # on envoie
    try:
        resp = urllib.request.urlopen(goto)
    except urllib.error.HTTPError as e:
        print(e.code, return_keys[e.code])
    print(resp.status, resp.reason, return_keys[resp.status])


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
                    prog='FreeMobile SMS',
                    description='Send a message to a referenced user')
    parser.add_argument('message')
    parser.add_argument('-u', '--user')
    args = parser.parse_args()
    send_sms(args.message, user=args.user)
