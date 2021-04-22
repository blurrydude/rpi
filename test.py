import tkinter as tk
import paho.mqtt.client as mqtt
import time
import socket

circuits = {
    "A1": {"id": "A1", "address": "shelly1pm-8CAAB574C489", "relay":"0"     , "label":"Fireplace"}, #192.168.1.60 - Fireplace Lights
    "B1": {"id": "B1", "address": "shelly1pm-84CCA8A11963", "relay":"0"     , "label":"Lamp post"}, #192.168.1.62 - Lamp Post and Driveway
    "C1": {"id": "C1", "address": "shellyswitch25-8CAAB55F44D6", "relay":"0", "label":"Porch"}, #192.168.1.243 - Porch Light
    "C2": {"id": "C2", "address": "shellyswitch25-8CAAB55F44D6", "relay":"1", "label":"Dining Room"}, #192.168.1.243 - Dining Room Light
    "D1": {"id": "D1", "address": "shellyswitch25-8CAAB55F405D", "relay":"0", "label":"Office Fan"}, #192.168.1.242 - Office Fan
    "D2": {"id": "D2", "address": "shellyswitch25-8CAAB55F405D", "relay":"1", "label":"Kitchen"}, #192.168.1.242 - Kitchen Lights
    "E1": {"id": "E1", "address": "shellyswitch25-8CAAB55F3B3F", "relay":"0", "label":"Office Lights"}, #192.168.1.244 - Office Lights
    "E2": {"id": "E2", "address": "shellyswitch25-8CAAB55F3B3F", "relay":"1", "label":"Unknown 1"}, #192.168.1.244 - Unknown
    "F1": {"id": "F1", "address": "shellyswitch25-8CAAB55F4553", "relay":"0", "label":"Unknown 2"}, #192.168.1.245 - Unknown
    "F2": {"id": "F2", "address": "shellyswitch25-8CAAB55F4553", "relay":"1", "label":"Bar"}, #192.168.1.245 - Bar Lights
    "G1": {"id": "G1", "address": "shellyswitch25-8CAAB55F44D7", "relay":"0", "label":"Unknown 3"}, #192.168.1.61  - Unknown
    "G2": {"id": "G2", "address": "shellyswitch25-8CAAB55F44D7", "relay":"1", "label":"Unknown 4"}, #192.168.1.61  - Unknown
    "H1": {"id": "H1", "address": "shellyswitch25-8CAAB561DDED", "relay":"0", "label":"Guest Bathroom"}, #192.168.1.240 - Bathroom Lights and Fan
    "H2": {"id": "H2", "address": "shellyswitch25-8CAAB561DDED", "relay":"1", "label":"Garage Lights"}, #192.168.1.240 - Garage Lights
    "I1": {"id": "I1", "address": "shellyswitch25-8CAAB561DDCF", "relay":"0", "label":"Master Bath"}, #192.168.1.241 - Master Bath Lights
    "I2": {"id": "I2", "address": "shellyswitch25-8CAAB561DDCF", "relay":"1", "label":"Stairway"}, #192.168.1.241 - Stairway Lights
    "J1": {"id": "J1", "address": "shellyswitch25-8CAAB55F402F", "relay":"0", "label":"Hallway"}, #192.168.1.239 - Hallway
    "J2": {"id": "J2", "address": "shellyswitch25-8CAAB55F402F", "relay":"1", "label":"Shower Fan"} #192.168.1.239 - Master Bath Vent Fan
}

map = {
    "Bedroom": {
        "portals": ["Master Bath", "Hallway"],
        "circuits": ["E2","F1","G1","G2"]
    },
    "Master Bath": {
        "portals": ["Bedroom"],
        "circuits": ["I1","J2"]
    },
    "Hallway": {
        "portals": ["Bedroom","Bathroom","Library","Workout Room","Living Room"],
        "circuits": ["J1"]
    },
    "Bathroom": {
        "portals": ["Hallway"],
        "circuits": ["H1"]
    },
    "Library": {
        "portals": ["Hallway"],
        "circuits": []
    },
    "Workout Room": {
        "portals": ["Hallway"],
        "circuits": []
    },
    "Living Room": {
        "portals": ["Hallway","Kitchen","Dining Room"],
        "circuits": ["A1","B1","C1"]
    },
    "Kitchen": {
        "portals": ["Living Room","Shop","Dining Room"],
        "circuits": ["D2","F2"]
    },
    "Dining Room": {
        "portals": ["Kitchen","Game Room","Office"],
        "circuits": ["C2"]
    },
    "Game Room": {
        "portals": ["Dining Room","Deck"],
        "circuits": []
    },
    "Office": {
        "portals": ["Dining Room","Deck"],
        "circuits": ["D1","E1"]
    },
    "Shop": {
        "portals": ["Kitchen","Laundry Room","Electronics Room"],
        "circuits": ["H2","I2"]
    },
    "Laundry Room": {
        "portals": ["Shop"],
        "circuits": []
    },
    "Electronics Room": {
        "portals": ["Shop"],
        "circuits": []
    }
}

myname = socket.gethostname()
############# CONFIG #############
broker = "192.168.1.22"
##################################
current_room = "Living Room"
client = mqtt.Client()
window = tk.Tk()
#window.attributes("-fullscreen", 1)
greetingvar = tk.StringVar()
greetingvar.set('MQTT Control Switch - '+current_room)
greeting = tk.Label(textvariable=greetingvar, bg="black", fg="white")
greeting.grid(row=0, columnspan=4)

def mosquittoDo(topic, command):
    try:
        print("publishing '"+command+"' to "+topic)
        client.connect(broker)
        client.publish(topic,command)
        client.disconnect()
    except:
        print("BAD - Failed to publish "+command+" to "+topic)

def room_click(id):
    gotoroom(id)

def on_click(cid):
    print("on_click: "+cid)
    circuit = circuits[cid]
    print("circuit.label: "+circuit["label"])
    topic = "shellies/"+circuit["address"]+"/relay/"+circuit["relay"]+"/command"
    mosquittoDo(topic,"on")

def off_click(cid):
    print("off_click: "+cid)
    circuit = circuits[cid]
    print("circuit.label: "+circuit["label"])
    topic = "shellies/"+circuit["address"]+"/relay/"+circuit["relay"]+"/command"
    mosquittoDo(topic,"off")

def gotoroom(roomname):
    global current_room
    global greetingvar
    room = map[current_room]
    for button in room["buttons"]:
        button.grid_forget()
    for button in room["onbuttons"]:
        button.grid_forget()
    for button in room["offbuttons"]:
        button.grid_forget()
    for label in room["labels"]:
        label.grid_forget()
    current_room = roomname
    greetingvar.set('MQTT Control Switch - '+current_room)
    room = map[current_room]
    r = 1
    for button in room["buttons"]:
        button.grid(row=r, column=0)
        r = r + 1
    r = 1
    for label in room["labels"]:
        label.grid(row=r, column=1)
        r = r + 1
    r = 1
    for button in room["onbuttons"]:
        button.grid(row=r, column=2)
        r = r + 1
    r = 1
    for button in room["offbuttons"]:
        button.grid(row=r, column=3)
        r = r + 1
button = []
onbutton = []
offbutton = []
label = []
b = 0
nb = 0
for roomkey in map.keys():
    room = map[roomkey]
    map[roomkey]["buttons"] = []
    map[roomkey]["onbuttons"] = []
    map[roomkey]["offbuttons"] = []
    map[roomkey]["labels"] = []
    for portal in room["portals"]:
        button.append(tk.Button(text=portal,command=lambda id=portal: room_click(id), height=3, width=40))
        map[roomkey]["buttons"].append(button[b])
        b = b + 1
    for cid in room["circuits"]:
        circuit = circuits[cid]
        label.append(tk.Label(text=circuit["label"]))
        onbutton.append(tk.Button(text="ON",command=lambda id=cid: on_click(id), height=3, width=40))
        offbutton.append(tk.Button(text="OFF",command=lambda id=cid: off_click(id), height=3, width=40))
        map[roomkey]["onbuttons"].append(onbutton[nb])
        map[roomkey]["offbuttons"].append(offbutton[nb])
        map[roomkey]["labels"].append(label[nb])
        nb = nb + 1
gotoroom(current_room)
window.mainloop()