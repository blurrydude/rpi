# import requests
# import json
# from requests.models import HTTPBasicAuth
# import os
# # import subprocess
# # import time

# # repeat = False

# # for i in range(3):
# #     print("waiting "+str(i))
# #     time.sleep(1)

# # if repeat is True:
# #     #os.system("python3 test.py")
# #     subprocess.Popen(["python3","test.py"])
# #     print("after")
# # print("exiting")
# # exit()

# #print(os.path.dirname(os.path.realpath(__file__)))

# #set_mqtt = "settings/mqtt?mqtt_server=192.168.1.200:1883"

# # passwords = json.load(open("SmarterCircuits/secrets.json"))
# # circuits = json.load(open("SmarterCircuits/circuits.json"))
# # motion_sensors = json.load(open("SmarterCircuits/motionsensors.json"))
# # door_sensors = json.load(open("SmarterCircuits/doorsensors.json"))
# # ht_sensors = json.load(open("SmarterCircuits/thsensors.json"))
# # ips = {}
# # output = {}
# # for circuit in circuits:
# #     ip = circuit["ip_address"]
# #     id = circuit["id"]
# #     if id not in passwords.keys():
# #         print("NOT FOUND: "+id)
# #         continue
# #     r = requests.get("http://"+ip+"/status", auth=HTTPBasicAuth('admin', passwords[id]))
# #     raw = r.text
# #     data = json.loads(raw)
# #     ison = data["relays"][int(circuit["relay_id"])]["ison"]
# #     power = data["meters"][int(circuit["relay_id"])]["power"]
# #     print(id+": "+str(ison)+" - "+str(power))

# # class SubThing:
# #     def __init__(self):
# #         self.subattrA = "a"
# #         self.subattrB = "b"

# # class Thing:
# #     def __init__(self):
# #         self.attrA = "a"
# #         self.attrB = SubThing()

# # thing = Thing()
# # for attr, value in thing.__dict__.items():
# #     print(attr)
# #     print(type(value) == object)

# import smtplib

# to = ['smartercircuits@gmail.com']
# subject = 'Lorem ipsum dolor sit amet'
# body = 'consectetur adipiscing elit'

# class NotifyService:
#     @staticmethod
#     def send_email(to, subject, body):
#         email_text = """\
#         From: %s
#         To: %s
#         Subject: %s

#         %s
#         """ % ('house@smartercirctuis.com', ", ".join(to), subject, body)

#         try:
#             smtp_server = smtplib.SMTP('smtp.mailgun.com', 587)
#             smtp_server.starttls()
#             smtp_server.login()
#             smtp_server.sendmail('house@smartercirctuis.com', to, email_text)
#             smtp_server.quit()
#             print ("Email sent successfully!")
#         except Exception as ex:
#             print ("Something went wrong….",ex)

thing1 = [True,True]
thing2 = [True,True]
thing3 = [False,True]
test12 = thing1 == thing2
test23 = thing2 == thing3
print(test12)
print(test23)