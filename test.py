import requests
from requests.models import HTTPBasicAuth
#import os
# import subprocess
# import time

# repeat = False

# for i in range(3):
#     print("waiting "+str(i))
#     time.sleep(1)

# if repeat is True:
#     #os.system("python3 test.py")
#     subprocess.Popen(["python3","test.py"])
#     print("after")
# print("exiting")
# exit()

#print(os.path.dirname(os.path.realpath(__file__)))

r = requests.get("http://192.168.1.130/settings", auth=HTTPBasicAuth('admin', 'pkg2kjg!ydh@nat.NZT'))
print(r.text)