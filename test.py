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

# thing1 = [True,True]
# thing2 = [True,True]
# thing3 = [False,True]
# test12 = thing1 == thing2
# test23 = thing2 == thing3
# print(test12)
# print(test23)

# import requests
# r =requests.get('https://api.idkline.com/state')
# print(r.text)

# import paho.mqtt.client as mqtt
# import json
# import time

# client = mqtt.Client()

# circuit_authority = "192.168.1.224"

# def on_message(client, userdata, message):
#     global circuit_authority
#     topic = message.topic
#     text = str(message.payload.decode("utf-8"))
#     name = topic.split("/")[2]
#     peer = json.loads(text)
#     if peer["circuit_authority"] is True and circuit_authority != peer["ip_address"]:
#         circuit_authority = peer["ip_address"]
#         print("circuit authority set: "+circuit_authority)

# def connectMqtt():
#     global client
#     client.connect("192.168.1.200")
#     client.on_message = on_message
#     client.on_disconnect = connectMqtt
#     client.subscribe("smarter_circuits/peers/#")
#     client.loop_start()
#     while True:
#         time.sleep(1)

# connectMqtt()

import socket
from urllib import request, parse

IPS = ('192.168.1.40','192.168.1.41','192.168.1.42','192.168.1.43')
for IP in IPS:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((IP, 4028))
    c = "{\"command\":\"stats\"}"
    s.send(c.encode('utf-8'))
    data = s.recv(2048).decode('utf-8')
    # f.close()
    data = format(data)
    x = data.split("id\":1}")
    y = x[0].replace("}{","},{")+"id\":1}"
    s.close()
    # f = open(IP.replace(".","_")+".json", "w")
    # f.write(y)
    # f.close()
    #y = y.encode('utf-8')
    print(y)
    #URL = "https://script.google.com/a/blurrydude.com/macros/s/AKfycbxT-EbiUIEFF8oldf30E-8CxQQHyYx_wK3xxl6Ui4lQ/dev"
    # URL = "https://script.google.com/macros/s/AKfycbxDlO5-s2uKougMR5axSUF-aTRxRlVbvkbWT8o-N3SyBKpfBd0n/exec"
    # PARAMS = parse.urlencode({'data':y,'miner':IP.replace(".","_")}).encode()
    # req = request.Request(URL,data=PARAMS)
    # res = request.urlopen(req)
    # print (res.read())

exit()