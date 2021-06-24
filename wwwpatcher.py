import os
import time
import os.path
from os import path
import datetime

def doCheck():
    os.system('cd /var/www/hiveseven.com/hive-seven && git pull origin master')
    time.sleep(9)
    repo_version_file = '/var/www/hiveseven.com/hive-seven/version.txt'
    local_version_file = '/var/www/hiveseven.com/hive-seven/version.txt'
    with open(repo_version_file, "r") as read_file:
        repo_version = read_file.read()
    if path.exists(local_version_file) == False:
        with open(local_version_file, "w") as write_file:
            write_file.write("0.1")

    with open(local_version_file, "r") as read_file:
        local_version = read_file.read()

    now = datetime.datetime.now()
    if local_version != repo_version or (now.hour == 0 and now.minute == 0):
        with open(local_version_file, "w") as write_file:
            write_file.write(repo_version)
        time.sleep(1)
        os.system('ng build')
        exit()

doCheck()