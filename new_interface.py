import tkinter as tk
import paho.mqtt.client as mqtt

circuits = [
    {"address": "shelly1pm-8CAAB574C489", "relay":"0"     , "label":"Fireplace"}, #192.168.1.60 - Fireplace Lights
    {"address": "shelly1pm-84CCA8A11963", "relay":"0"     , "label":"Lamp post"}, #192.168.1.62 - Lamp Post and Driveway
    {"address": "shellyswitch25-8CAAB55F44D6", "relay":"0", "label":"Porch"}, #192.168.1.243 - Porch Light
    {"address": "shellyswitch25-8CAAB55F44D6", "relay":"1", "label":"Dining Room"}, #192.168.1.243 - Dining Room Light
    {"address": "shellyswitch25-8CAAB55F405D", "relay":"0", "label":"Office Fan"}, #192.168.1.242 - Office Fan
    {"address": "shellyswitch25-8CAAB55F405D", "relay":"1", "label":"Kitchen"}, #192.168.1.242 - Kitchen Lights
    {"address": "shellyswitch25-8CAAB55F3B3F", "relay":"0", "label":"Office Lights"}, #192.168.1.244 - Office Lights
    {"address": "shellyswitch25-8CAAB55F3B3F", "relay":"1", "label":"Livingroom TV"}, #192.168.1.244 - Livingroom TV Outlet
    {"address": "shellyswitch25-8CAAB55F4553", "relay":"0", "label":"Gym Lamp"}, #192.168.1.245 - Gym Lamp Outlet
    {"address": "shellyswitch25-8CAAB55F4553", "relay":"1", "label":"Bar"}, #192.168.1.245 - Bar Lights
    {"address": "shellyswitch25-8CAAB55F44D7", "relay":"0", "label":"Bedroom Lamp"}, #192.168.1.61  - Bedroom Lamp Outlet
    {"address": "shellyswitch25-8CAAB55F44D7", "relay":"1", "label":"Library Lamp"}, #192.168.1.61  - Library Lamp Outlet
    {"address": "shellyswitch25-8CAAB561DDED", "relay":"0", "label":"Guest Bathroom"}, #192.168.1.240 - Bathroom Lights and Fan
    {"address": "shellyswitch25-8CAAB561DDED", "relay":"1", "label":"Garage Lights"}, #192.168.1.240 - Garage Lights
    {"address": "shellyswitch25-8CAAB561DDCF", "relay":"0", "label":"Master Bath"}, #192.168.1.241 - Master Bath Lights
    {"address": "shellyswitch25-8CAAB561DDCF", "relay":"1", "label":"Stairway"}, #192.168.1.241 - Stairway Lights
    {"address": "shellyswitch25-8CAAB55F402F", "relay":"0", "label":"Hallway"}, #192.168.1.239 - Hallway
    {"address": "shellyswitch25-8CAAB55F402F", "relay":"1", "label":"Shower Fan"}, #192.168.1.239 - Master Bath Vent Fan
    {"address": "", "relay":"1", "label":"SYSTEM"} 
]

current_circuit = 0
broker = "192.168.1.22"
client = mqtt.Client()

def mosquittoDo(topic, command):
    client.connect(broker)
    try:
        print("publishing '"+command+"' to "+topic)
        client.publish(topic,command)
    except:
        print("BAD - Failed to publish "+command+" to "+topic)
    client.disconnect()

def on_click():
    print("on_click")
    c = circuits[current_circuit]
    if c["label"] == "SYSTEM":
        return
    topic = "shellies/"+c["address"]+"/relay/"+c["relay"]+"/command"
    mosquittoDo(topic,"on")

def off_click():
    print("off_click")
    c = circuits[current_circuit]
    if c["label"] == "SYSTEM":
        exit()
    topic = "shellies/"+c["address"]+"/relay/"+c["relay"]+"/command"
    mosquittoDo(topic,"off")

def previous_switch():
    global current_circuit
    print("previous_switch")
    if current_circuit == 0:
        current_circuit = len(circuits) - 1
    else:
        current_circuit = current_circuit - 1
    c = circuits[current_circuit]
    print("switch to "+c["label"])
    switch_label.set(c["label"])
    

def next_switch():
    global current_circuit
    print("next_switch")
    if current_circuit == len(circuits) - 1:
        current_circuit = 0
    else:
        current_circuit = current_circuit + 1
    c = circuits[current_circuit]
    print("switch to "+c["label"])
    switch_label.set(c["label"])

window = tk.Tk()
button1label = tk.StringVar()
button2label = tk.StringVar()
switch_label = tk.StringVar()
width = window.winfo_screenwidth()
height = window.winfo_screenheight()

window.attributes("-fullscreen", 1)
window.geometry(str(width)+"x"+str(height))
window.columnconfigure(0, minsize=width*0.1)
window.columnconfigure(1, minsize=width*0.8)
window.columnconfigure(2, minsize=width*0.1)

switch_label.set("Fireplace")
button1label.set("ON")
button2label.set("OFF")

left = tk.Button(text="<",command=lambda id=0: previous_switch(), height=2, font = ("Times", 24))
left.grid(row=0, column=0, sticky="ew", padx=5, pady=2)

switchlabel = tk.Label(textvariable=switch_label, font=("Times", 32))
switchlabel.grid(row=0, column=1, sticky="nesw", pady=5, padx=5)

right = tk.Button(text=">",command=lambda id=0: next_switch(), height=2, font = ("Times", 24))
right.grid(row=0, column=2, sticky="ew", padx=5, pady=2)

onbutton = tk.Button(textvariable=button1label,command=lambda id=0: on_click(), height=3, font = ("Times", 32))
onbutton.grid(row=2, column=1, sticky="ew", padx=5, pady=2)

offbutton = tk.Button(textvariable=button2label,command=lambda id=0: off_click(), height=3, font = ("Times", 32))
offbutton.grid(row=3, column=1, sticky="ew", padx=5, pady=2)

window.mainloop()