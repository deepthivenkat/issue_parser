#!/usr/bin/python
import datetime
import time
from subprocess import call

import os
from git import Repo, GitCommandError

path = os.path.dirname(os.path.realpath(__file__))


def run_db_migration():
    current_ts = time.time()
    time_stamp = datetime.datetime.fromtimestamp(current_ts).strftime('%Y-%m-%d-%H:%M:%S')
    issue_backup_db = 'issues_backup_' + time_stamp + '.db'
    repo = Repo(path)
    assert not repo.bare
    assert repo.refs['origin/master'] == repo.remotes.origin.refs.master
    origin = repo.remotes.origin
    index = repo.index
    db_path = path + '/backup_db'
    if os.path.exists(path + '/issues.db'):
        if os.path.exists(db_path) and os.path.isdir(db_path):
            #           check if a previous version of a backup exist and delete it
            print 'Backup database already exists. Removing older version of the back up'
            call('rm -r backup_db', shell=True)
            call('git rm -r backup_db/.', shell=True)
        print 'Switching to branch : master'
        call('mkdir backup_db', shell=True)
        try:
            repo.heads.master.checkout()
        except GitCommandError:
            print 'Please make sure your current branch is clean and all the changes are either committed or stashed' \
                  'before switching to master branch'

        call('mv issues.db backup_db/' + issue_backup_db, shell=True)
        index.add([path + '/backup_db/' + issue_backup_db])
        index.commit('Adding new backup database at ' + time_stamp)
        # push the backup database file to master branch of the repository
        origin.push()
        call('python extract_id_title_url.py 1', shell=True)
        call('python run.py&', shell=True)
        time.sleep(60)
        call('python dump_webcompat_to_db.py 1', shell=True)
    else:
        raise IOError('FileNotFound : No database file found to backup. Please run python run.py to create the db file')

if __name__ == '__main__':
    WATCHED_FILES = [path + '/issues.db']
    WATCHED_FILES_MTIMES = [(f, time.ctime(os.path.getmtime(f))) for f in WATCHED_FILES]
    #   Read the last modified time property of the issues.db file. If there is any change, run the migration script
    while True:
        for f, mtime in WATCHED_FILES_MTIMES:
            if time.ctime(os.path.getmtime(f)) != mtime:
                run_db_migration()
        time.sleep(36000)
