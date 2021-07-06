import tkinter as tk
dev = True
if dev == False:
    import paho.mqtt.client as mqtt

circuits = [
    {"address": "shellyswitch25-8CAAB55F44D7", "relay":"0", "label":"Bedroom Lamp"}, #192.168.1.61  - Bedroom Lamp Outlet
    {"address": "shellyswitch25-8CAAB561DDCF", "relay":"0", "label":"Master Bath"}, #192.168.1.241 - Master Bath Lights
    {"address": "shellyswitch25-8CAAB55F402F", "relay":"1", "label":"Shower Fan"}, #192.168.1.239 - Master Bath Vent Fan
    {"address": "shellyswitch25-8CAAB55F402F", "relay":"0", "label":"Hallway"}, #192.168.1.239 - Hallway
    {"address": "shellyswitch25-8CAAB561DDED", "relay":"0", "label":"Guest Bathroom"}, #192.168.1.240 - Bathroom Lights and Fan
    {"address": "shellyswitch25-8CAAB55F44D7", "relay":"1", "label":"Library Lamp"}, #192.168.1.61  - Library Lamp Outlet
    {"address": "shellyswitch25-8CAAB55F4553", "relay":"0", "label":"Gym Lamp"}, #192.168.1.245 - Gym Lamp Outlet
    {"address": "shellyswitch25-8CAAB55F3B3F", "relay":"1", "label":"Livingroom TV"}, #192.168.1.244 - Livingroom TV Outlet
    {"address": "shelly1pm-84CCA8A11963", "relay":"0"     , "label":"Lamp post"}, #192.168.1.62 - Lamp Post and Driveway
    {"address": "shellyswitch25-8CAAB55F44D6", "relay":"0", "label":"Porch"}, #192.168.1.243 - Porch Light
    {"address": "shelly1pm-8CAAB574C489", "relay":"0"     , "label":"Fireplace"}, #192.168.1.60 - Fireplace Lights
    {"address": "shellyswitch25-8CAAB55F44D6", "relay":"1", "label":"Dining Room"}, #192.168.1.243 - Dining Room Light
    {"address": "shellyswitch25-8CAAB55F405D", "relay":"1", "label":"Kitchen"}, #192.168.1.242 - Kitchen Lights
    {"address": "shellyswitch25-8CAAB55F4553", "relay":"1", "label":"Bar"}, #192.168.1.245 - Bar Lights
    {"address": "shellyswitch25-8CAAB55F405D", "relay":"0", "label":"Office Fan"}, #192.168.1.242 - Office Fan
    {"address": "shellyswitch25-8CAAB55F3B3F", "relay":"0", "label":"Office Lights"}, #192.168.1.244 - Office Lights
    {"address": "shellyswitch25-8CAAB561DDED", "relay":"1", "label":"Garage Lights"}, #192.168.1.240 - Garage Lights
    {"address": "shellyswitch25-8CAAB561DDCF", "relay":"1", "label":"Stairway"}, #192.168.1.241 - Stairway Lights
    {"address": "", "relay":"1", "label":"SYSTEM"} 
]

modes = [
    {"label":"Morning","circuits":[None,None,None,None,None,None,None,None,False,False,False,False,True,True,None,None,True,False]},
    {"label":"Dark","circuits":[False,False,False,False,False,False,False,None,False,False,False,False,False,False,False,False,False,False]},
    {"label":"Lunch","circuits":[None,None,None,None,None,None,None,None,None,None,None,True,True,True,None,None,False,True]},
    {"label":"Shower","circuits":[True,True,True,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None]},
    {"label":"Evening","circuits":[True,True,False,True,False,False,False,None,True,True,True,False,False,True,None,False,False,True]},
    {"label":"Night","circuits":[False,False,False,False,False,False,False,None,True,True,False,False,False,False,None,False,False,True]},
    {"label":"Alert","circuits":[True,True,True,True,True,True,True,None,True,True,True,True,True,True,None,True,True,True]}
]
current_mode = 0
current_circuit = 0
broker = "192.168.1.22"
client = None
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
    for ci in range(0,len(m["circuits"])):
        v = m["circuits"][ci]
        if v is None:
            continue
        co = "off"
        if v is True:
            co = "on"
        c = circuits[ci]
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

systeminfo = tk.Label(text="You can cycle through modes with the bottom left button and use the bottom right to set one.", font=("Times", 16), bg='black', fg='white')
systeminfo2 = tk.Label(text="Pressing OFF will exit this software.", font=("Times", 16), bg='black', fg='white')

window.mainloop()