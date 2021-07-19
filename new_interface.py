import tkinter as tk
dev = False
if dev == False:
    import paho.mqtt.client as mqtt

circuits = [
    #192.168.1.61  - Bedroom Lamp Outlet
    {"address": "shellyswitch25-8CAAB55F44D7", "relay":"0", "label":"Bedroom Lamp", 
    "onModes": ["Shower", "Evening", "Alert"],
    "offModes":["Dark", "Night", "Day"],
    "zones":["All", "Master Bedroom", "Second Floor"]},

    #192.168.1.241 - Master Bath Lights
    {"address": "shellyswitch25-8CAAB561DDCF", "relay":"0", "label":"Master Bath",
    "onModes": ["Morning", "Shower", "Evening", "Alert"],
    "offModes":["Dark", "Night"],
    "zones":["All", "Master Bath", "Second Floor"]}, 

    #192.168.1.239 - Master Bath Vent Fan
    {"address": "shellyswitch25-8CAAB55F402F", "relay":"1", "label":"Shower Fan",
    "onModes": ["Shower"],
    "offModes":["Dark", "Night", "Alert"],
    "zones":["All", "Master Bath", "Second Floor"]}, 

    #192.168.1.239 - Hallway
    {"address": "shellyswitch25-8CAAB55F402F", "relay":"0", "label":"Hallway",
    "onModes": ["Morning", "Lunch","Evening", "Alert"],
    "offModes":["Dark", "Night", "Day"],
    "zones":["All", "Hallway", "Second Floor"]}, 

    #192.168.1.240 - Bathroom Lights and Fan
    {"address": "shellyswitch25-8CAAB561DDED", "relay":"0", "label":"Guest Bathroom",
    "onModes": ["Alert"],
    "offModes":["Dark", "Night"],
    "zones":["All", "Guest Bathroom", "Second Floor"]}, 

    #192.168.1.61  - Library Lamp Outlet
    {"address": "shellyswitch25-8CAAB55F44D7", "relay":"1", "label":"Library Lamp",
    "onModes": ["Alert", "Evening"],
    "offModes":["Dark", "Night"],
    "zones":["All", "Library", "Second Floor"]}, 

    #192.168.1.245 - Gym Lamp Outlet
    {"address": "shellyswitch25-8CAAB55F4553", "relay":"0", "label":"Gym Lamp",
    "onModes": ["Morning", "Evening", "Alert"],
    "offModes":["Dark", "Lunch", "Night"],
    "zones":["All", "Gym", "Second Floor"]}, 

    #{"address": "shellyswitch25-8CAAB55F3B3F", "relay":"1", "label":"Livingroom TV"}, #192.168.1.244 - Livingroom TV Outlet

    #192.168.1.x - Living Room Lamp
    {"address": "shelly1pm-68C63AFB315A", "relay":"0", "label":"Livingroom Lamp",
    "onModes": ["Evening", "Alert"],
    "offModes":["Dark", "Evening", "Night", "Day"],
    "zones":["All", "Living Room", "First Floor"]}, 

    #192.168.1.62 - Lamp Post and Driveway
    {"address": "shelly1pm-84CCA8A11963",      "relay":"0", "label":"Lamp post",
    "onModes": ["Evening", "Night", "Alert"],
    "offModes":["Morning", "Dark", "Lunch", "Day"],
    "zones":["All", "Front Yard", "Exterior"]}, 

    #192.168.1.243 - Porch Light
    {"address": "shellyswitch25-8CAAB55F44D6", "relay":"0", "label":"Porch",
    "onModes": ["Evening", "Night", "Alert"],
    "offModes":["Morning", "Dark", "Lunch", "Day"],
    "zones":["All", "Front Yard", "Exterior"]}, 

    #192.168.1.60 - Fireplace Lights
    {"address": "shelly1pm-8CAAB574C489",      "relay":"0", "label":"Fireplace",
    "onModes": ["Evening", "Alert", "Dinner"],
    "offModes":["Dark", "Night", "Day"],
    "zones":["All", "Living Room", "First Floor"]}, 

    #192.168.1.243 - Dining Room Light
    {"address": "shellyswitch25-8CAAB55F44D6", "relay":"1", "label":"Dining Room",
    "onModes": ["Morning", "Lunch", "Alert", "Dinner"],
    "offModes":["Dark", "Night", "Evening", "Day"],
    "zones":["All", "Dining Room", "First Floor"]}, 

    #192.168.1.165 - Game Room Lights
    {"address": "shelly1pm-C82B961DD3B1",      "relay":"0", "label":"Game Room",
    "onModes": ["Morning", "Evening", "Alert", "Dinner"],
    "offModes":["Dark", "Night", "Day"],
    "zones":["All", "Game Room", "First Floor"]}, 

    #192.168.1.x - Game Tables
    {"address": "shelly1pm-68C63AFB726B", "relay":"0", "label":"Game Tables",
    "onModes": ["Morning", "Evening", "Alert"],
    "offModes":["Dark", "Night", "Day"],
    "zones":["All", "Game Room", "First Floor"]}, 

    #192.168.1.242 - Kitchen Lights
    {"address": "shellyswitch25-8CAAB55F405D", "relay":"1", "label":"Kitchen",
    "onModes": ["Morning", "Lunch", "Alert", "Dinner"],
    "offModes":["Dark", "Evening", "Night", "Day"],
    "zones":["All", "Kitchen", "First Floor"]}, 

    #192.168.1.x - Coffee Station
    {"address": "shelly1pm-F4CFA2747F54", "relay":"0", "label":"Coffee Station",
    "onModes": ["Morning", "Lunch", "Dinner", "Evening", "Night", "Alert"],
    "offModes":["Dark", "Day"],
    "zones":["All", "Kitchen", "Counters", "First Floor"]}, 

    #192.168.1.x - Under Cabinet Lights
    {"address": "shelly1pm-68C63AFB6B0A", "relay":"0", "label":"Under Cabinet",
    "onModes": ["Morning", "Lunch", "Dinner", "Alert"],
    "offModes":["Dark", "Night", "Evening", "Day"],
    "zones":["All", "Kitchen", "Counters", "First Floor"]}, 

    #192.168.1.245 - Bar Lights
    {"address": "shellyswitch25-8CAAB55F4553", "relay":"1", "label":"Bar",
    "onModes": ["Morning", "Lunch", "Dinner", "Evening", "Alert"],
    "offModes":["Dark", "Night", "Day"],
    "zones":["All", "Kitchen", "First Floor"]}, 

    #192.168.1.242 - Office Fan
    {"address": "shellyswitch25-8CAAB55F405D", "relay":"0", "label":"Office Fan",
    "onModes": [],
    "offModes":["Alert"],
    "zones":["All", "Ventilation", "Office", "First Floor"]}, 

    #192.168.1.244 - Office Lights
    {"address": "shellyswitch25-8CAAB55F3B3F", "relay":"0", "label":"Office Lights",
    "onModes": ["Morning", "Lunch", "Dinner", "Evening", "Alert"],
    "offModes":["Dark", "Night", "Day"],
    "zones":["All", "Office", "First Floor"]}, 

    #192.168.1.240 - Garage Lights
    {"address": "shellyswitch25-8CAAB561DDED", "relay":"1", "label":"Garage Lights",
    "onModes": ["Morning", "Lunch", "Evening", "Alert"],
    "offModes":["Dark", "Night", "Day"],
    "zones":["All", "Garage"]}, 

    #192.168.1.241 - Stairway Lights
    {"address": "shellyswitch25-8CAAB561DDCF", "relay":"1", "label":"Stairway",
    "onModes": ["Morning", "Lunch", "Dinner", "Night", "Alert", "Day"],
    "offModes":["Dark", "Evening", "Night"],
    "zones":["All", "Garage"]}, 

    #192.168.1.170 - Bench Fan
    {"address": "shelly1pm-68C63AFB6BD5", "relay":"0", "label":"Bench Fan",
    "onModes": [],
    "offModes":["Alert"],
    "zones":["All", "Ventilation", "First Floor"]}, 
    
    {"address": "", "relay":"1", "label":"SYSTEM",
    "onModes": [],
    "offModes":[],
    "zones":[]} 
]

modes = ["Morning", "Day", "Lunch", "Day", "Dinner", "Evening", "Shower", "Night", "Dark", "Alert"]
current_mode = 0
current_circuit = 0
broker = "192.168.1.22"
client =  None
if dev == False:
    client = mqtt.Client()

def mosquittoDo(topic, command):
    if dev == False:
        client.connect(broker)
    try:
        print("publishing '"+command+"' to "+topic)
        if dev == False:
            client.publish(topic,command)
    except:
        print("BAD - Failed to publish "+command+" to "+topic)
    if dev == False:
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
    if c["label"] == "SYSTEM":
        hide_on_button()
        show_system_info()
    else:
        hide_system_info()
        show_on_button()
    

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
    if c["label"] == "SYSTEM":
        hide_on_button()
        show_system_info()
    else:
        hide_system_info()
        show_on_button()

def cycle_mode():
    global current_mode
    if current_mode == len(modes)-1:
        current_mode = 0
    else:
        current_mode = current_mode + 1
    m = modes[current_mode]
    mode_label.set(m["label"])

def set_mode():
    m = modes[current_mode]
    for ci in range(0,len(circuits)):
        c = circuits[ci]
        co = None
        if m in c["onModes"]:
            co = "on"
        if m in c["offModes"]:
            co = "off"
        if co is None:
            return
        topic = "shellies/"+c["address"]+"/relay/"+c["relay"]+"/command"
        mosquittoDo(topic,co)

def show_on_button():
    onbutton.grid(row=2, column=1, sticky="ew", padx=5, pady=2)

def hide_on_button():
    onbutton.grid_forget()

def show_system_info():
    systeminfo.grid(row=2, column=1, sticky="nesw", padx=5, pady=2)
    systeminfo2.grid(row=3, column=1, sticky="nesw", padx=5, pady=2)
    offbutton.grid_forget()
    offbutton.grid(row=4, column=1, sticky="ew", padx=5, pady=2)
    bottomleft.grid_forget()
    bottomleft.grid(row=5, column=0, sticky="ew", padx=5, pady=2)
    bottomright.grid_forget()
    bottomright.grid(row=5, column=2, sticky="ew", padx=5, pady=2)
    modelabel.grid_forget()
    modelabel.grid(row=5, column=1, sticky="nesw", pady=5, padx=5)

def hide_system_info():
    systeminfo.grid_forget()
    systeminfo2.grid_forget()
    offbutton.grid_forget()
    offbutton.grid(row=3, column=1, sticky="ew", padx=5, pady=2)
    bottomleft.grid_forget()
    bottomleft.grid(row=4, column=0, sticky="ew", padx=5, pady=2)
    bottomright.grid_forget()
    bottomright.grid(row=4, column=2, sticky="ew", padx=5, pady=2)
    modelabel.grid_forget()
    modelabel.grid(row=4, column=1, sticky="nesw", pady=5, padx=5)

window = tk.Tk()
button1label = tk.StringVar()
button2label = tk.StringVar()
switch_label = tk.StringVar()
mode_label = tk.StringVar()
width = window.winfo_screenwidth()
height = window.winfo_screenheight()

window.attributes("-fullscreen", 1)
window.geometry(str(width)+"x"+str(height))
window.configure(bg='black')
window.columnconfigure(0, minsize=width*0.1)
window.columnconfigure(1, minsize=width*0.8)
window.columnconfigure(2, minsize=width*0.1)

switch_label.set(circuits[current_circuit]["label"])
mode_label.set(modes[current_mode]["label"])
button1label.set("ON")
button2label.set("OFF")

left = tk.Button(text="<",command=lambda id=0: previous_switch(), height=2, font = ("Times", 24), bg='#5555aa', fg='black')
left.grid(row=0, column=0, sticky="ew", padx=5, pady=2)

switchlabel = tk.Label(textvariable=switch_label, font=("Times", 32), bg='black', fg='white')
switchlabel.grid(row=0, column=1, sticky="nesw", pady=5, padx=5)

right = tk.Button(text=">",command=lambda id=0: next_switch(), height=2, font = ("Times", 24), bg='#5555aa', fg='black')
right.grid(row=0, column=2, sticky="ew", padx=5, pady=2)

onbutton = tk.Button(textvariable=button1label,command=lambda id=0: on_click(), height=3, font = ("Times", 32), bg='#55aa55', fg='black')
show_on_button()

offbutton = tk.Button(textvariable=button2label,command=lambda id=0: off_click(), height=3, font = ("Times", 32), bg='#aa5555', fg='black')
offbutton.grid(row=3, column=1, sticky="ew", padx=5, pady=2)

bottomleft = tk.Button(text="^",command=lambda id=0: cycle_mode(), height=2, font = ("Times", 24), bg='#5555aa', fg='black')
bottomleft.grid(row=4, column=0, sticky="ew", padx=5, pady=2)

bottomright = tk.Button(text="set",command=lambda id=0: set_mode(), height=2, font = ("Times", 20), bg='#5555aa', fg='black')
bottomright.grid(row=4, column=2, sticky="ew", padx=5, pady=2)

modelabel = tk.Label(textvariable=mode_label, font=("Times", 24), bg='black', fg='white')
modelabel.grid(row=4, column=1, sticky="nesw", pady=5, padx=5)

systeminfo = tk.Label(text="", font=("Times", 16), bg='black', fg='white')
systeminfo2 = tk.Label(text="Pressing OFF will exit this software.", font=("Times", 16), bg='black', fg='white')

window.mainloop()