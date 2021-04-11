import os
import time
def doCheck():
    os.system('cd /home/pi/rpi && git pull --all')
    time.sleep(9)
    repo_version_file = '/home/pi/rpi/rpi_version.txt'
    local_version_file = '/home/pi/rpi_version.txt'
    with open(repo_version_file, "r") as read_file:
        repo_version = read_file.read()
    if path.exists(local_version_file) == False:
        with open(local_version_file, "w") as write_file:
            write_file.write("0.1")

    with open(local_version_file, "r") as read_file:
        local_version = read_file.read()

    if local_version != repo_version:
        with open(local_version_file, "w") as write_file:
            write_file.write(repo_version)
        time.sleep(1)
        os.system('sudo reboot now')
        exit()

doCheck()