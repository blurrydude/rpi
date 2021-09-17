import json
from datetime import datetime
import os

class SmarterLog:
    @staticmethod
    def log(origin, message):
        if type(message) is not type(""):
            message = json.dumps(message)
        timestamp = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        logfiledate = datetime.now().strftime("%Y%m%d%H")
        logfile = "logs/SmarterCircuits_"+logfiledate+".log"
        entry = timestamp + " [" + origin + "]: " + message + "\n"
        print(entry)
        if os.path.exists(logfile):
            append_write = 'a' # append if already exists
        else:
            append_write = 'w' # make a new file if not

        with open(logfile, append_write) as write_file:
            write_file.write(entry)