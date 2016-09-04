#!/usr/bin/env python3

import server, sys, os, shutil, time, datetime, argparse, traceback

ts = time.time()
delim = '/'

def create_new_user(email):
    try:
        server.create_user(email, 'zpoatkp')
    except:
        print('An error has occured when creating a new user.')

def reset_password(email):
    try:
        server.change_password(email, 'zpoatkp')
    except:
        print('An error has occured when resetting the user\'s password.')

def lock_user(email):
    try:
        server.lock_user(email)
    except:
        print('An error has occured when locking the user.')

def unlock_user(email):
    try:
        server.unlock_user(email)
    except:
        print('An error has occured when unlocking the user.')

def delete_user(email):
    try:
        server.delete_user(email)
    except:
        print('An error has occured when deleting the user.')

def rm_dirs():
    server.file_engine.rm_dirs()

def setup_dirs():
    server.file_engine.setup_dirs()

def clean_logs():
    server.file_engine.log_cleanup()

def backup_files():
    try:
        shutil.make_archive(delim.join(['/docuserv', 'backups', 'files', 'files.' + datetime.datetime.fromtimestamp(ts).strftime('%Y.%m.%d.%H.%M.%S')]), 'zip', '/docuserv/files')
    except:
        print('An error has occured when backing files up.')
        traceback.print_exc()

def backup_sql():
    try:
        shutil.copyfile('/docuserv/zd.db', delim.join(['/docuserv', 'backups', 'sqllite', 'zd.' + datetime.datetime.fromtimestamp(ts).strftime('%Y.%m.%d.%H.%M.%S') + '.db']))
    except:
        print('An error has occured when backing files up.')
        traceback.print_exc()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Docuserv utilities.')
    parser.add_argument('-b', help='Backup database and files', action='store_true', dest='backup')
    parser.add_argument('-x', help='Clean files archive', action='store_true', dest='rm_dirs')
    parser.add_argument('-o', help='Generate files archive', action='store_true', dest='mk_dirs')
    parser.add_argument('-y', help='Clean logfiles', action='store_true', dest='clean_logs')
    parser.add_argument('-c', help='Create new user', action='store', dest='new_user')
    parser.add_argument('-r', help='Reset user\'s email', action='store', dest='reset_user')
    parser.add_argument('-l', help='Lock a user out', action='store', dest='lock_user')
    parser.add_argument('-u', help='Unlock a user', action='store', dest='unlock_user')
    parser.add_argument('-d', help='Delete a user', action='store', dest='delete_user')

    args = parser.parse_args()


    if args.backup:
        backup_files()
        backup_sql()

    if args.new_user != None:
        assert '@' in args.new_user
        create_new_user(args.new_user)
        shutil.copyfile('/var/docuserv/zd.db', '/docuserv/zd.db')
        open('/docuserv/data_update', 'a')

    if args.reset_user != None:
        assert '@' in args.reset_user
        reset_password(args.reset_user)
        shutil.copyfile('/var/docuserv/zd.db', '/docuserv/zd.db')
        open('/docuserv/data_update', 'a')

    if args.lock_user != None:
        assert '@' in args.lock_user
        lock_user(args.lock_user)
        shutil.copyfile('/var/docuserv/zd.db', '/docuserv/zd.db')
        open('/docuserv/data_update', 'a')

    if args.unlock_user != None:
        assert '@' in args.unlock_user
        unlock_user(args.unlock_user)
        shutil.copyfile('/var/docuserv/zd.db', '/docuserv/zd.db')
        open('/docuserv/data_update', 'a')

    if args.delete_user != None:
        assert '@' in args.delete_user
        delete_user(args.delete_user)
        shutil.copyfile('/var/docuserv/zd.db', '/docuserv/zd.db')
        open('/docuserv/data_update', 'a')

    if args.rm_dirs:
        rm_dirs()

    if args.mk_dirs:
        setup_dirs()

    if args.clean_logs:
        clean_logs()
