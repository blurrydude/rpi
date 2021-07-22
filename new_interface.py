import time
time.sleep(120)
import tkinter as tk
import json
dev = False
if dev == False:
    import paho.mqtt.client as mqtt

f = open('circuits.json',)
circuits = json.load(f)
circuits.append({"notes":"","address": "", "relay":"1", "label":"SYSTEM",
    "onModes": [],
    "offModes":[],
    "zones":[]})

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
    mode_label.set(m)

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
mode_label.set(modes[current_mode])
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