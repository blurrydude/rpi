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

# #set_mqtt = "settings/mqtt?mqtt_server=192.168.2.200:1883"

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
#39567751
#43139231
#40566491
#40312181
#40009901
#41563901
#39737841


# import random
# from PIL import Image, ImageDraw

# # Constants for the size of the image
# WIDTH = 500
# HEIGHT = 500

# # Create an image to draw on
# image = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
# draw = ImageDraw.Draw(image)

# # Generate a random number of rectangles
# num_rectangles = random.randint(1, 10)

# # Generate random rectangles
# for i in range(num_rectangles):
#     # Generate random dimensions and position for the rectangle
#     x = random.randint(0, WIDTH-1)
#     y = random.randint(0, HEIGHT-1)
#     w = random.randint(1, WIDTH-x)
#     h = random.randint(1, HEIGHT-y)

#     # Generate a random color for the rectangle
#     r = random.randint(0, 255)
#     g = random.randint(0, 255)
#     b = random.randint(0, 255)
#     color = (r, g, b)

#     # Draw the rectangle
#     draw.rectangle((x, y, x+w, y+h), fill=color)

# # Save the image
# image.save("rectangles.bmp")
# print("Saved image to rectangles.bmp")





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
#     client.connect("192.168.2.200")
#     client.on_message = on_message
#     client.on_disconnect = connectMqtt
#     client.subscribe("smarter_circuits/peers/#")
#     client.loop_start()
#     while True:
#         time.sleep(1)

# connectMqtt()

# import socket
# from urllib import request, parse

# IPS = ('192.168.1.40','192.168.1.41','192.168.1.42','192.168.1.43')
# for IP in IPS:
#     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     s.connect((IP, 4028))
#     c = "{\"command\":\"stats\"}"
#     s.send(c.encode('utf-8'))
#     data = s.recv(2048).decode('utf-8')
#     # f.close()
#     data = format(data)
#     x = data.split("id\":1}")
#     y = x[0].replace("}{","},{")+"id\":1}"
#     s.close()
#     # f = open(IP.replace(".","_")+".json", "w")
#     # f.write(y)
#     # f.close()
#     #y = y.encode('utf-8')
#     print(y)
#     #URL = "https://script.google.com/a/blurrydude.com/macros/s/AKfycbxT-EbiUIEFF8oldf30E-8CxQQHyYx_wK3xxl6Ui4lQ/dev"
#     # URL = "https://script.google.com/macros/s/AKfycbxDlO5-s2uKougMR5axSUF-aTRxRlVbvkbWT8o-N3SyBKpfBd0n/exec"
#     # PARAMS = parse.urlencode({'data':y,'miner':IP.replace(".","_")}).encode()
#     # req = request.Request(URL,data=PARAMS)
#     # res = request.urlopen(req)
#     # print (res.read())

# exit()

# import subprocess

# stuff = [
#     #"https://winsupplyinc.visualstudio.com/DefaultCollection/ACA/_git/ACA",
#     "ACA_ParseAck",
#     "ACAExportFromOnBase",
#     "ACAManifest",
#     "AcqPayroll",
#     "AIMHandler",
#     "AMDA",
#     "AMDAConcatenator",
#     "AnnualReportConcatenation",
#     "AnnualReportImport",
#     "APPDUpdateOB",
#     "APPortalAPI",
#     "APVendorMerge",
#     "ArchiveCompany",
#     "AreaLeaderEmail",
#     "BI-RDL",
#     "CloudOCR_ParseXML",
#     "CloudOCR_VendorFile",
#     "CopyReceiver",
#     "DeletedDoubleCheck",
#     "DocumentData",
#     "DocumentValidationOBandMF",
#     "DW_SQLServerObjects",
#     "e941Helper",
#     "e941Processor",
#     "FITServices",
#     "FixVIRMismatch",
#     "FootnoteData",
#     "GetOBDocumentData",
#     "ImportLIFO",
#     "IOWN_CreateDummyInvoices",
#     "IOWNProcessor",
#     "IOWNReconciliation",
#     "IOWNSummary",
#     "IRSCaller",
#     "IRSTransmission",
#     "ItemReassign",
#     "LIFOParsing",
#     "LocalCompanyInformationUpdate",
#     "LoggingService",
#     "OBStorageService",
#     "OBTauliaWebService",
#     "ODWInvoiceImport",
#     "OnBase%20Disk%20Validation",
#     "OnBase%20Health%20Check",
#     "OnBase.Utilities.OBCheckRunAudit",
#     "OnBase_ImportWCMS",
#     "OnBaseDataMigration",
#     "OnbaseEditor",
#     "OnBaseUserCopy",
#     "ParseEDI",
#     "ParsePayments",
#     "ParsePayments_CorrectItemNums",
#     "ParsePayments_UpdateOnBase",
#     "POSync",
#     "Processors.Rebates.PopulateVendors",
#     "R2R%20Import",
#     "Rebates_FindPayables",
#     "Rebates_VendorReportProcessor",
#     "REMS_CompanyInfoUpdate",
#     "RoadmapImport",
#     "Service.WSS.BackorderManagement",
#     "ServiceCheck",
#     "Services.Lookup.DocumentData",
#     "Services.Mainframe.DirectDeposit",
#     "Services.Mainframe.GetCurrentFinancialPeriod",
#     "Services.OnBase.DebitMemo",
#     "Services.OnBase.DebitMemoCore",
#     "Services.OnBase.DocumentData",
#     "Services.OnBase.DocumentUpload",
#     "Services.OnBase.GetDebitMemoList",
#     "Services.OnBase.GetUserGroups",
#     "Services.OnBase.GLAccount",
#     "Services.OnBase.InvoiceNbr",
#     "Services.OnBase.InvoiceTerms",
#     "Services.OnBase.IOWN",
#     "Services.OnBase.LocalCompanyInfo",
#     "Services.OnBase.LocalCompanyLookup",
#     "Services.OnBase.MatchableDebits",
#     "Services.OnBase.MTR",
#     "Services.OnBase.ReconciliationToReceiver",
#     "Services.OnBase.UPSData",
#     "Services.OnBase.ValidateVendor",
#     "Services.OnBase.VEA",
#     "Services.OnBase.VendorAutocomplete",
#     "Services.OnBase.VendorAutofillUpdates",
#     "Services.OnBase.VendorLocations",
#     "Services.OnBase.VendorLookup",
#     "Services.OnBase.VendorUpdate",
#     "Services.OnBase.WIPA_ForceMatch",
#     "Services.OnBase.WIPA_VIR",
#     "Services.OnBase.WISE_DebitMemo",
#     "Services.RebatesManagement",
#     "Services.REMS.LocalCompanyFinancials",
#     "Services.REMS.PIFTransmission",
#     "Services.REMS.REMSData",
#     "Services.Taulia.BusinessUnit",
#     "Services.Taulia.EarlyPayment",
#     "Services.Taulia.Invoices",
#     "Services.Taulia.Payment",
#     "Services.Taulia.PurchaseOrder",
#     "Services.Taulia.Supplier",
#     "Services.WebpageToPDF",
#     "Services.WSS.JCIForecast",
#     "TauliaDynamicDiscountReport",
#     "TauliaUtil_Invoice",
#     "TauliaUtil_PO",
#     "tcaccessTest",
#     "Test",
#     "TWM_MatchEngineLegacy",
#     "UnitySchedulerErrorNotifications",
#     "UnityTaskSchedulerAutoClearError",
#     "UpdateMFVendorData",
#     "UpdateTTMAutofill",
#     "UpdateVendorInfoForms",
#     "UPSInvoiceProcessing",
#     "Utility.APEDI_Audit",
#     "Utility.IOWN_GetCompanyData",
#     "Utility.IOWNReconciliation",
#     "Utility.UpdateKeyword",
#     "VoidReissueProcessing",
#     "What",
#     "Win.Taulia.Standard",
#     "WinReportService",
#     "WIPA_MatchEngine",
#     "WIPA_MatchEngineExtreme"
# ]

# for thing in stuff:
#     place = thing.split('/')
#     place = place[len(place)-1]
#     subprocess.call("git clone https://winsupplyinc.visualstudio.com/DefaultCollection/"+thing+"/_git/"+thing+" C:/WINREPO/"+place)

# import os
# rootdir = 'C:/WINREPO/'

# term = "https://onbasews1.winwholesale.com/"#GetCurrentFinancialPeriod/api/financial/period"

# targets = []

# for subdir, dirs, files in os.walk(rootdir):
#     for file in files:
#         p = os.path.join(subdir, file)
#         if file.endswith(".cs"):
#             try:
#                 f = open(p,mode='r')
#                 text = f.read().lower()
#                 f.close()
#                 if term.lower() in text:
#                     targets.append(p)
#             except:
#                 print("can't read "+p)

# print(targets)

# import json


# class DewData:
#     def __init__(self, tc, h, wpdc=2):
#         self.temperature_c = tc
#         self.temperature_f = CtoF(tc)
#         self.humidity = h
#         self.dew_point_c = tc - ((100-h)/5)
#         self.dew_point_f = CtoF(self.dew_point_c)
#         self.delta_c = self.temperature_c - self.dew_point_c
#         # assume 20 degrees costs 40W / 12V = 3.333~A OR 1 degree costs 2W / 12V = 0.167A
#         self.watt_cost = self.delta_c * wpdc
#         self.amps_at_12v = self.watt_cost / 12
#     def toJSON(self):
#         return json.dumps(self, default=lambda o: o.__dict__,
#             sort_keys=True, indent=4)

# def get_dew_point_f(tf, rh):
#     TC = FtoC(tf)
#     Td = TC - ((100-rh)/5)
#     dp = CtoF(Td)
#     print(str(tf)+ "F ("+str(TC)+" C) @ "+str(rh)+" % RH Dew Point: "+str(dp)+" F ("+str(Td)+" C) "+str(TC-Td)+" C drop")
#     return dp

# def FtoC(f):
#     return round((f - 32) * (5 / 9), 2)

# def CtoF(c):
#     return round((c * (9 / 5)) + 32, 2)

# watt_per_degree_celsius = 5
# # matrix = []
# # for t in range(-20,130):
# #     r = []
# #     for h in range(1,20):
# #         dew_data = json.loads(DewData(t,h*5, watt_per_degree_celsius).toJSON())
# #         r.append(dew_data)
# #     matrix.append(r)
# # with open("dew_data.json","w") as write_file:
# #     write_file.write(json.dumps(matrix, indent=4))

# tf = 31
# rh = 34
# print(DewData(tf,rh, watt_per_degree_celsius).toJSON())

# a = (1,1)
# b = (2,3)
# print(a + b)