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

circuit_state = {
    "A1": False,
    "B1": False,
    "C1": False,
    "C2": False,
    "D1": False,
    "D2": False,
    "E1": False,
    "E2": False,
    "F1": False,
    "F2": False,
    "G1": False,
    "G2": False,
    "H1": False,
    "H2": False,
    "I1": False,
    "I2": False,
    "J1": False,
    "J2": False
}

map = {
    "Bedroom": {
        "portals": ["Master Bath", "Hallway"],
        "circuits": ["E2","F1","G1","G2"],
        "rgb": ["windowpi"],
        "buttons": [],
        "onbuttons": [],
        "offbuttons": [],
        "rgbbuttons": [],
        "labels": []
    },
    "Master Bath": {
        "portals": ["Bedroom"],
        "circuits": ["I1","J2"],
        "rgb": [],
        "buttons": [],
        "onbuttons": [],
        "offbuttons": [],
        "rgbbuttons": [],
        "labels": []
    },
    "Hallway": {
        "portals": ["Bedroom","Bathroom","Library","Workout Room","Living Room"],
        "circuits": ["J1"],
        "rgb": [],
        "buttons": [],
        "onbuttons": [],
        "offbuttons": [],
        "rgbbuttons": [],
        "labels": []
    },
    "Bathroom": {
        "portals": ["Hallway"],
        "circuits": ["H1"],
        "rgb": [],
        "buttons": [],
        "onbuttons": [],
        "offbuttons": [],
        "rgbbuttons": [],
        "labels": []
    },
    "Library": {
        "portals": ["Hallway"],
        "circuits": [],
        "rgb": [],
        "buttons": [],
        "onbuttons": [],
        "offbuttons": [],
        "rgbbuttons": [],
        "labels": []
    },
    "Workout Room": {
        "portals": ["Hallway"],
        "circuits": [],
        "rgb": [],
        "buttons": [],
        "onbuttons": [],
        "offbuttons": [],
        "rgbbuttons": [],
        "labels": []
    },
    "Living Room": {
        "portals": ["Hallway","Kitchen","Dining Room"],
        "circuits": ["A1","B1","C1"],
        "rgb": ["canvaspi"],
        "buttons": [],
        "onbuttons": [],
        "offbuttons": [],
        "rgbbuttons": [],
        "labels": []
    },
    "Kitchen": {
        "portals": ["Living Room","Shop","Dining Room"],
        "circuits": ["D2","F2"],
        "rgb": [],
        "buttons": [],
        "onbuttons": [],
        "offbuttons": [],
        "rgbbuttons": [],
        "labels": []
    },
    "Dining Room": {
        "portals": ["Kitchen","Game Room","Office"],
        "circuits": ["C2"],
        "rgb": [],
        "buttons": [],
        "onbuttons": [],
        "offbuttons": [],
        "rgbbuttons": [],
        "labels": []
    },
    "Game Room": {
        "portals": ["Dining Room","Deck"],
        "circuits": [],
        "rgb": ["clockpi","gameroompi"],
        "buttons": [],
        "onbuttons": [],
        "offbuttons": [],
        "rgbbuttons": [],
        "labels": []
    },
    "Office": {
        "portals": ["Dining Room","Deck"],
        "circuits": ["D1","E1"],
        "rgb": [],
        "buttons": [],
        "onbuttons": [],
        "offbuttons": [],
        "rgbbuttons": [],
        "labels": []
    },
    "Shop": {
        "portals": ["Kitchen","Laundry Room","Electronics Room"],
        "circuits": ["H2","I2"],
        "rgb": [],
        "buttons": [],
        "onbuttons": [],
        "offbuttons": [],
        "rgbbuttons": [],
        "labels": []
    },
    "Laundry Room": {
        "portals": ["Shop"],
        "circuits": [],
        "rgb": [],
        "buttons": [],
        "onbuttons": [],
        "offbuttons": [],
        "rgbbuttons": [],
        "labels": []
    },
    "Electronics Room": {
        "portals": ["Shop"],
        "circuits": [],
        "rgb": [],
        "buttons": [],
        "onbuttons": [],
        "offbuttons": [],
        "rgbbuttons": [],
        "labels": []
    }
}

colors = [
    {"label":"white","command":"0:255:255:255"},
    {"label":"red","command":"0:255:0:0"},
    {"label":"green","command":"0:0:255:0"},
    {"label":"blue","command":"0:0:0:255"},
    {"label":"orange","command":"0:255:64:0"},
    {"label":"purple","command":"0:255:0:255"},
    {"label":"teal","command":"0:0:255:255"},
    {"label":"off","command":"0:0:0:0"},
    {"label":"gradient","command":"3:0"},
    {"label":"rainbow","command":"4:0"},
    {"label":"random pixels","command":"5:0"},
    {"label":"random change","command":"6:0"},
    {"label":"swipe change","command":"7:0"}
]
reverse_lookup = {} #I can't figure out a better or faster way
text_var = {}
myname = socket.gethostname()
############# CONFIG #############
broker = "192.168.1.22"
button_height = 1
base_font = ("Times", 12)
header_font = ("Times", 16)
##################################
current_room = "Living Room"
client = mqtt.Client()
window = tk.Tk()
window.attributes("-fullscreen", 1)
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
column_width = screen_width / 4
window.columnconfigure(0, minsize=column_width)
window.columnconfigure(1, minsize=column_width)
window.columnconfigure(2, minsize=column_width)
window.columnconfigure(3, minsize=column_width)
onbutton = {}
offbutton = {}
label = {}
ready = False

greetingvar = tk.StringVar()
greetingvar.set(current_room)
greeting = tk.Label(textvariable=greetingvar, font=header_font)
greeting.grid(row=0, column=1, sticky="nesw", pady=4)

def on_message(client, userdata, message):
    global text_var
    global circuit_state
    if ready is not True:
        return
    result = str(message.payload.decode("utf-8"))
    topic = message.topic
    cid = reverse_lookup[topic]
    previous = circuit_state[cid]
    if result == "on":
        circuit_state[cid] = True
        text_var[cid+"ON"].set("[[[ ON ]]]")
        text_var[cid+"OFF"].set("OFF")
    else:
        circuit_state[cid] = False
        text_var[cid+"ON"].set("ON")
        text_var[cid+"OFF"].set("[[[ OFF ]]]")
    # if circuit_state[cid] != previous:
    #     gotoroom(current_room)

def mosquittoDo(topic, command):
    try:
        print("publishing '"+command+"' to "+topic)
        client.publish(topic,command)
    except:
        print("BAD - Failed to publish "+command+" to "+topic)

def rgb_click(id, command):
    mosquittoDo(id+'/commands',command)

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
    # for button in room["buttons"]:
    #     button.grid_forget()
    for button in room["rgbbuttons"]:
        button.grid_forget()
    for button in room["onbuttons"]:
        button.grid_forget()
    for button in room["offbuttons"]:
        button.grid_forget()
    for label in room["labels"]:
        label.grid_forget()
    current_room = roomname
    greetingvar.set(current_room)
    room = map[current_room]
    r = 1
    for label in room["labels"]:
        label.grid(row=r, column=1, sticky="ew", padx=2, pady=2)
        r = r + 1
    r = 1
    for button in room["onbuttons"]:
        button.grid(row=r, column=2, sticky="ew", padx=2, pady=2)
        r = r + 1
    r = 1
    for button in room["offbuttons"]:
        button.grid(row=r, column=3, sticky="ew", padx=2, pady=2)
        r = r + 1
    c = 2
    for button in room["rgbbuttons"]:
        button.grid(row=r, column=c, sticky="ew", padx=2, pady=2)
        if c == 2:
            c = 3
        else:
            r = r + 1
            c = 2

if __name__ == "__main__":
    subscriptions = []
    for k in circuits.keys():
        c = circuits[k]
        addy = "shellies/"+c["address"]+"/relay/"+c["relay"]
        print("preparing "+addy)
        subscriptions.append((addy, 0))
        reverse_lookup[addy] = k
    connected = False
    while connected is False:
        try:
            client.on_message = on_message
            client.connect(broker)
            client.subscribe(subscriptions)
            client.loop_start()
            connected = True
        except:
            print("BAD - client failed connection. Will try again in five seconds")
            connected = False
            time.sleep(5)
    b = 0
    for roomkey in map.keys():
        room = map[roomkey]
        button = tk.Button(text=roomkey,command=lambda id=roomkey: room_click(id), height=button_height, font=base_font)
        button.grid(row=b+1, column=0, sticky="ew", padx=2, pady=2)
        b = b + 1
        for cid in room["circuits"]:
            circuit = circuits[cid]
            text_var[cid+"ON"] = tk.StringVar()
            text_var[cid+"OFF"] = tk.StringVar()
            text_var[cid+"ON"].set("ON")
            text_var[cid+"OFF"].set("OFF")
            label[cid] = tk.Label(text=circuit["label"], font=base_font)
            onbutton[cid] = tk.Button(textvariable=text_var[cid+"ON"],command=lambda id=cid: on_click(id), height=button_height, font=base_font)
            offbutton[cid] = tk.Button(textvariable=text_var[cid+"OFF"],command=lambda id=cid: off_click(id), height=button_height, font=base_font)
            map[roomkey]["onbuttons"].append(onbutton[cid])
            map[roomkey]["offbuttons"].append(offbutton[cid])
            map[roomkey]["labels"].append(label[cid])
        for rgb in room["rgb"]:
            for color in colors:
                map[roomkey]["rgbbuttons"].append(tk.Button(text=color["label"],command=lambda id=rgb, command=color["command"]: rgb_click(id, command), height=button_height, font=base_font))
    gotoroom(current_room)
    ready = True
    window.mainloop()
    try:
        client.loop_stop()
        client.disconnect()
    except:
        print("INFO - Client diconnet failed. Maybe, the connection failed first or during runtime.")