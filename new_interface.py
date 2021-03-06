#! /usr/bin/env python3
import paho.mqtt.client as mqtt
import time
time.sleep(10)
from os import write
import tkinter as tk
import json
import requests

class SmartScreen:
    global current_func
    global current_mode
    def __init__(self):
        self.buttons = []
        self.labels = []
    def onclick(self, button):
        #print(button.text)
        if "screen" in button.func:
            switchToScreen(button.target)
        if "circuit" in button.func:
            toggleCircuit(button.target)
        if "zone" in button.func:
            setZone(button.target)
        if "mode" in button.func:
            setMode(button.target)
        if "reload" in button.func:
            loadConfig()
            switchToScreen("main")
        if "exit" in button.func:
            exit()
        if "toggle" in button.func:
            com = "turn "
            if current_func == "zone":
                com = com + " zone "
            com = com + button.func.replace("toggle","") + " " + current_target.lower()
            sendCommand(com)
        if "increase_low_temp" in button.func:
            increase_low_temp(button.target)
        if "increase_high_temp" in button.func:
            increase_high_temp(button.target)
        if "decrease_low_temp" in button.func:
            decrease_low_temp(button.target)
        if "decrease_high_temp" in button.func:
            decrease_high_temp(button.target)
        if "shades" in button.func:
            sendCommand(button.target + " the shades")
        if "system_switch" in button.func:
            toggle_system(button.target)
    def hide(self):
        for button in self.buttons:
            button.hide()
        for label in self.labels:
            label.hide()
    def draw(self):
        for button in self.buttons:
            button.redraw()
        for label in self.labels:
            label.redraw()

class SmartButton:
    def __init__(self, screen, jsond):
        self.screen = screen
        self.text = jsond["text"]
        self.func = jsond["func"]
        self.target = jsond["target"]
        self.height = jsond["height"]
        self.fontname = jsond["fontname"]
        self.fontsize = jsond["fontsize"]
        self.bg = jsond["bg"]
        self.fg = jsond["fg"]
        self.row = jsond["row"]
        self.col = jsond["col"]
        self.sticky = jsond["sticky"]
        self.padx = jsond["padx"]
        self.pady = jsond["pady"]
        self.__make__()
    def __make__(self):
        self.button = tk.Button(text=self.text,command=lambda d=self: self.screen.onclick(d), height=self.height, font = (self.fontname, self.fontsize), bg=self.bg, fg=self.fg)
    def show(self):
        self.button.grid(row=self.row, column=self.col, sticky=self.sticky, padx=self.padx, pady=self.pady)
    def hide(self):
        self.button.grid_forget()
    def redraw(self):
        self.hide()
        self.__make__()
        self.show()

class SmartLabel:
    def __init__(self, jsond):
        self.text = jsond["text"]
        self.fontname = jsond["fontname"]
        self.fontsize = jsond["fontsize"]
        self.bg = jsond["bg"]
        self.fg = jsond["fg"]
        self.row = jsond["row"]
        self.col = jsond["col"]
        self.sticky = jsond["sticky"]
        self.padx = jsond["padx"]
        self.pady = jsond["pady"]
        self.__make__()
    def __make__(self):
        self.label = tk.Label(text=self.text, font = (self.fontname, self.fontsize), bg=self.bg, fg=self.fg)
    def show(self):
        self.label.grid(row=self.row, column=self.col, sticky=self.sticky, padx=self.padx, pady=self.pady)
    def hide(self):
        self.label.grid_forget()
    def redraw(self):
        self.hide()
        self.__make__()
        self.show()

def loadConfig():
    global circuits
    global config
    global screens

    if screens is not None:
        for scrn in screens.keys():
            s = screens[scrn]
            for b in s.buttons:
                b.hide()
            for l in s.labels:
                l.hide()
            screens[scrn] = None

    try:
        f = open('/home/pi/rpi/circuits.json')
        circuits = json.load(f)

        cf = open('/home/pi/rpi/interface_config.json')
        config = json.load(cf)
    except:
        f = open('circuits.json')
        circuits = json.load(f)

        cf = open('interface_config.json')
        config = json.load(cf)
        
    screens = {}
    for screenname in config.keys():
        screenconfig = config[screenname]
        screen = SmartScreen()
        for buttonconfig in screenconfig["buttons"]:
            button = SmartButton(screen, buttonconfig)
            screen.buttons.append(button)
        for labelconfig in screenconfig["labels"]:
            label = SmartLabel(labelconfig)
            screen.labels.append(label)
        screens[screenname] = screen
    
    buildCircuitScreens()

    buildToggleScreen()

    buildStatusScreen()

    buildThermostatScreen()

def buildThermostatScreen():
    global screens
    readings = getReadings()
    screens["thermostats"] = SmartScreen()
    screens["thermostats"].buttons.append(SmartButton(screens["thermostats"],{
                "text": "Main Menu", "func": "screen", "target":"main",
                "height": 1, "fontname": "Times", "fontsize": 20,
                "bg": "orange", "fg": "white", "sticky": "nesw",
                "row": 1, "col": 1, "padx": 5, "pady": 5
            }))
    screens["thermostats"].labels.append(SmartLabel({
                "text": "Thermostats", "bg": "black", "fg": "white",
                "fontname": "Times", "fontsize": 16, "sticky": "nesw",
                "row": 0, "col": 1, "padx": 5, "pady": 5
            }))
    row = 2
    for room in readings.keys():
        screens["thermostats"].buttons.append(SmartButton(screens["thermostats"],{
                    "text": room, "func": "screen", "target":room.lower()+"thermostat",
                    "height": 2, "fontname": "Times", "fontsize": 24,
                    "bg": "darkgreen", "fg": "white", "sticky": "nesw",
                    "row": row, "col": 1, "padx": 5, "pady": 5
                }))
        row = row + 1
        screens[room+"thermostat"] = SmartScreen()
        screens[room+"thermostat"].buttons.append(SmartButton(screens[room+"thermostat"],{
                    "text": "Back", "func": "screen", "target":"thermostats",
                    "height": 1, "fontname": "Times", "fontsize": 20,
                    "bg": "darkblue", "fg": "white", "sticky": "nesw",
                    "row": 1, "col": 1, "padx": 5, "pady": 5
                }))
        screens[room+"thermostat"].buttons.append(SmartButton(screens[room+"thermostat"],{
                    "text": "Increase", "func": "increase_low_temp", "target":room,
                    "height": 1, "fontname": "Times", "fontsize": 20,
                    "bg": "darkred", "fg": "white", "sticky": "nesw",
                    "row": 2, "col": 0, "padx": 5, "pady": 5
                }))
        screens[room+"thermostat"].buttons.append(SmartButton(screens[room+"thermostat"],{
                    "text": "Decrease", "func": "decrease_low_temp", "target":room,
                    "height": 1, "fontname": "Times", "fontsize": 20,
                    "bg": "darkblue", "fg": "white", "sticky": "nesw",
                    "row": 4, "col": 0, "padx": 5, "pady": 5
                }))
        screens[room+"thermostat"].buttons.append(SmartButton(screens[room+"thermostat"],{
                    "text": "Increase", "func": "increase_high_temp", "target":room,
                    "height": 1, "fontname": "Times", "fontsize": 20,
                    "bg": "darkred", "fg": "white", "sticky": "nesw",
                    "row": 2, "col": 2, "padx": 5, "pady": 5
                }))
        screens[room+"thermostat"].buttons.append(SmartButton(screens[room+"thermostat"],{
                    "text": "Decrease", "func": "decrease_high_temp", "target":room,
                    "height": 1, "fontname": "Times", "fontsize": 20,
                    "bg": "darkblue", "fg": "white", "sticky": "nesw",
                    "row": 4, "col": 2, "padx": 5, "pady": 5
                }))
        screens[room+"thermostat"].buttons.append(SmartButton(screens[room+"thermostat"],{
                    "text": "Toggle System", "func": "system_switch", "target":room,
                    "height": 1, "fontname": "Times", "fontsize": 20,
                    "bg": "darkblue", "fg": "white", "sticky": "nesw",
                    "row": 6, "col": 1, "padx": 5, "pady": 5
                }))
        screens[room+"thermostat"].labels.append(SmartLabel({
                    "text": "Heat When Below", "bg": "black", "fg": "white",
                    "fontname": "Times", "fontsize": 12, "sticky": "nesw",
                    "row": 1, "col": 0, "padx": 5, "pady": 5
                }))
        screens[room+"thermostat"].labels.append(SmartLabel({
                    "text": "Thermostat", "bg": "black", "fg": "white",
                    "fontname": "Times", "fontsize": 16, "sticky": "nesw",
                    "row": 0, "col": 1, "padx": 5, "pady": 5
                }))
        screens[room+"thermostat"].labels.append(SmartLabel({
                    "text": "Cool When Above", "bg": "black", "fg": "white",
                    "fontname": "Times", "fontsize": 12, "sticky": "nesw",
                    "row": 1, "col": 2, "padx": 5, "pady": 5
                }))
        screens[room+"thermostat"].labels.append(SmartLabel({
                    "text": "0 F", "bg": "black", "fg": "blue",
                    "fontname": "Times", "fontsize": 24, "sticky": "nesw",
                    "row": 3, "col": 0, "padx": 5, "pady": 5
                }))
        screens[room+"thermostat"].labels.append(SmartLabel({
                    "text": "0 F", "bg": "black", "fg": "white",
                    "fontname": "Times", "fontsize": 42, "sticky": "nesw",
                    "row": 3, "col": 1, "padx": 5, "pady": 5
                }))
        screens[room+"thermostat"].labels.append(SmartLabel({
                    "text": "0 F", "bg": "black", "fg": "red",
                    "fontname": "Times", "fontsize": 24, "sticky": "nesw",
                    "row": 3, "col": 2, "padx": 5, "pady": 5
                }))
        screens[room+"thermostat"].labels.append(SmartLabel({
                    "text": "stand_by", "bg": "black", "fg": "grey",
                    "fontname": "Times", "fontsize": 20, "sticky": "nesw",
                    "row": 4, "col": 1, "padx": 5, "pady": 5
                }))
        screens[room+"thermostat"].labels.append(SmartLabel({
                    "text": "", "bg": "black", "fg": "grey",
                    "fontname": "Times", "fontsize": 24, "sticky": "nesw",
                    "row": 5, "col": 1, "padx": 5, "pady": 5
                }))

def buildWorkingScreen():
    global screens
    screens["working"] = SmartScreen()
    screens["working"].labels.append(SmartLabel({
                "text": "please wait...", "bg": "black", "fg": "white",
                "fontname": "Times", "fontsize": 12, "sticky": "nesw",
                "row": 0, "col": 1, "padx": 5, "pady": 5
            }))
    screens["working"].labels.append(SmartLabel({
                "text": "Working", "bg": "black", "fg": "white",
                "fontname": "Times", "fontsize": 36, "sticky": "nesw",
                "row": 0, "col": 2, "padx": 5, "pady": 5
            }))

def buildStatusScreen():
    global screens
    screens["status"] = SmartScreen()
    screens["status"].buttons.append(SmartButton(screens["status"],{
                "text": "Main Menu", "func": "screen", "target":"main",
                "height": 1, "fontname": "Times", "fontsize": 20,
                "bg": "orange", "fg": "white", "sticky": "nesw",
                "row": 1, "col": 1, "padx": 5, "pady": 5
            }))
    screens["status"].labels.append(SmartLabel({
                "text": "Status", "bg": "black", "fg": "white",
                "fontname": "Times", "fontsize": 16, "sticky": "nesw",
                "row": 0, "col": 1, "padx": 5, "pady": 5
            }))
    screens["status"].labels.append(SmartLabel({
                "text": "Power: 0 W", "bg": "black", "fg": "white",
                "fontname": "Times", "fontsize": 24, "sticky": "nesw",
                "row": 0, "col": 2, "padx": 5, "pady": 5
            }))

def buildToggleScreen():
    global screens
    screens["toggle"] = SmartScreen()
    screens["toggle"].labels.append(SmartLabel({
                "text": "TOGGLE", "bg": "black", "fg": "white",
                "fontname": "Times", "fontsize": 16, "sticky": "nesw",
                "row": 0, "col": 1, "padx": 5, "pady": 5
            }))
    screens["toggle"].buttons.append(SmartButton(screens["toggle"], {
                "text": "Cancel", "func": "screen", "target":"main",
                "height": 2, "fontname": "Times", "fontsize": 20,
                "bg": "orange", "fg": "white", "sticky": "nesw",
                "row": 0, "col": 1, "padx": 5, "pady": 5
            }))
    screens["toggle"].buttons.append(SmartButton(screens["toggle"], {
                "text": "ON", "func": "toggleon", "target":"",
                "height": 4, "fontname": "Times", "fontsize": 20,
                "bg": "darkgreen", "fg": "white", "sticky": "nesw",
                "row": 1, "col": 1, "padx": 5, "pady": 5
            }))
    screens["toggle"].buttons.append(SmartButton(screens["toggle"], {
                "text": "OFF", "func": "toggleoff", "target":"",
                "height": 4, "fontname": "Times", "fontsize": 20,
                "bg": "darkred", "fg": "white", "sticky": "nesw",
                "row": 2, "col": 1, "padx": 5, "pady": 5
            }))

def buildCircuitScreens():
    global screens
    #circuit_screen.labels.append(SmartLabel({
    #            "text": "Circuits", "bg": "black", "fg": "white",
    #            "fontname": "Times", "fontsize": 16, "sticky": "nesw",
    #            "row": 0, "col": 1, "padx": 5, "pady": 5
    #        }))
    r = {}
    c = {}
    for circuit in circuits:
        lbl = circuit["label"]
        for zone in circuit["zones"]:
            id = zone.lower().replace(" ","")
            if id not in screens.keys():
                screens[id] = SmartScreen()
                screens[id].buttons.append(SmartButton(screens[id], 
                {
                    "text": "Back", "func": "screen", "target":"circuits",
                    "height": 2, "fontname": "Times", "fontsize": 20,
                    "bg": "orange", "fg": "white", "sticky": "nesw",
                    "row": 0, "col": 0, "padx": 5, "pady": 5
                }))
                r[id] = 0
                c[id] = 1
            screens[id].buttons.append(SmartButton(screens[id], 
                {
                    "text": lbl, "func": "circuit", "target":lbl,
                    "height": 2, "fontname": "Times", "fontsize": 20,
                    "bg": "darkgreen", "fg": "white", "sticky": "nesw",
                    "row": r[id], "col": c[id], "padx": 5, "pady": 5
                }))
            if c[id] < 2:
                c[id] = c[id] + 1
            else:
                c[id] = 0
                r[id] = r[id] + 1

def refreshStatusDetail():
    global status
    global power
    try:
        js =requests.get('https://api.idkline.com/states').text
        status = json.loads(js)
        js =requests.get('https://api.idkline.com/powerstates').text
        power = json.loads(js)
    except:
        print('failed to get status')

def switchToScreen(target):
    global current_screen
    #print("switchToScreen "+target)
    refreshStatusDetail()
    if current_screen != "":
        screens[current_screen].hide()
    if target == "status":
        w = 0
        for key in power.keys():
            p = round(float(power[key]))
            w = w + p
        screens["status"].labels[1].text = "Power: "+str(w)+" W"
        screens["status"].hide()
        r = len(screens["status"].labels)
        c = 0 #(r-2)%3
        while len(screens["status"].labels) < len(circuits)+2:
            screens["status"].labels.append(SmartLabel({
                "text": "", "bg": "black", "fg": "white",
                "fontname": "Times", "fontsize": 12, "sticky": "nesw",
                "row": r, "col": c, "padx": 5, "pady": 5
            }))
            if c == 2:
                c = 0
                r = r + 1
            else:
                c = c + 1
        i = 2
        for circuit in circuits:
            if circuit["label"] in status.keys() and circuit["label"] in power.keys():
                screens["status"].labels[i].text = circuit["label"] + " (" + status[circuit["label"]] + "): " + power[circuit["label"]] + " W"
                i = i + 1
    if target != "zones":
        for button in screens[target].buttons:
            if button.text in status.keys():
                if status[button.text] == "on":
                    button.bg = "darkgreen"
                else:
                    button.bg = "darkred"
    if "thermostat" in target and target != "thermostats":
        readings = getReadings()
        for room in readings.keys():
            reading = readings[room]
            screens[room+"thermostat"].labels[1].text = room + " thermostat"
            screens[room+"thermostat"].labels[4].text = str(reading["temperature"]) + " F"
            screens[room+"thermostat"].labels[3].text = str(reading["settings"]["temperature_low_setting"]) + " F"
            screens[room+"thermostat"].labels[5].text = str(reading["settings"]["temperature_high_setting"]) + " F"
            status_text = ""
            if reading["cooling"] == "on":
                status_text = status_text + " C"
            if reading["heating"] == "on":
                status_text = status_text + " H"
            if reading["circulation"] == "on":
                status_text = status_text + " A"
            if reading["whf"] == "on":
                status_text = status_text + " V"
            screens[room+"thermostat"].labels[6].text = str(reading["status"])
            screens[room+"thermostat"].labels[7].text = status_text
    if "modes" in target:
        mode = getMode()
        screens["modes"].labels[0].text = mode[0].upper()


    screens[target].draw()
    current_screen = target

def toggleCircuit(target):
    global current_func
    global current_target
    #print("toggleCircuit "+target)
    try:
        current_func = "circuit"
        current_target = target
        j =requests.get('https://api.idkline.com/states').text
        r = json.loads(j)
        if target in r.keys():
            com = "turn off " + target.lower()
            if r[target] == "off":
                com = "turn on " + target.lower()
            sendCommand(com)
            return
        else:
            screens["toggle"].labels[0].text = target
        screens["toggle"].hide()
        switchToScreen("toggle")
    except:
        print('failed to make request')

def setMode(target):
    #print("setMode "+target)
    sendCommand('set mode '+target)

def setZone(target):
    global current_func
    global current_target
    #print("setZone "+target)
    current_func = "zone"
    current_target = target
    switchToScreen("toggle")

def getReadings():
    try:
        r =requests.get('https://api.idkline.com/getreadings')
        data = json.loads(r.text)
        return data
    except:
        return None

def getMode():
    try:
        r =requests.get('https://api.idkline.com/getmode')
        data = json.loads(r.text)
        return data
    except:
        return "modes"

def sendCommand(command):
    mosquittoDo("smarter_circuits/command",command)
    #print("sending command: "+command)
    # try:
    #     r =requests.get('https://api.idkline.com/control/'+command)
    #     #print(str(r.status_code))
    #     switchToScreen("main")
    # except:
    #     print('failed to send command')

def mosquittoDo(topic, command):
    try:
        client = mqtt.Client()
        client.connect("192.168.2.200")
        client.publish(topic,command)
        client.disconnect()
    except:
        print('failed')
    return 'OK'

def increase_low_temp(room):
    #print("sending command: "+command)
    low = round(float(screens[room+"thermostat"].labels[3].text.replace(" F","")))
    high = round(float(screens[room+"thermostat"].labels[5].text.replace(" F","")))
    low = low + 1
    request = 'https://api.idkline.com/thermoset/'+room+'-'+str(low)+'-'+str(high)
    try:
        # switchToScreen("working")
        r =requests.get(request)
        screens[room+"thermostat"].labels[3].text = str(low) + " F"
        screens[room+"thermostat"].draw()
        # time.sleep(3)
    except:
        print('failed to send command: '+request)
    # switchToScreen(room+"thermostat")

def toggle_system(room):
    request = 'https://api.idkline.com/thermosettings/'+room
    response = requests.get(request)
    settings = json.loads(response.text)
    print("Original Value: "+str(settings["system_disabled"]))
    if settings["system_disabled"] is True:
        settings["system_disabled"] = False
    else:
        settings["system_disabled"] = True
    request = 'https://api.idkline.com/thermoset/'+room+'-'
    request = request + str(settings["temperature_low_setting"]) + '-'
    request = request + str(settings["temperature_high_setting"]) + '-'
    request = request + str(settings["humidity_setting"]) + '-'
    request = request + str(settings["air_circulation_minutes"]) + '-'
    request = request + str(settings["circulation_cycle_minutes"]) + '-'
    request = request + str(settings["stage_limit_minutes"]) + '-'
    request = request + str(settings["stage_cooldown_minutes"]) + '-'
    request = request + str(settings["swing_temp_offset"]) + '-'
    request = request + str(settings["ventilation_cycle_minutes"]) + '-'
    request = request + str(settings["system_disabled"]).lower()
    print("Sending Request: "+request)
    response = requests.get(request)

def increase_high_temp(room):
    #print("sending command: "+command)
    low = round(float(screens[room+"thermostat"].labels[3].text.replace(" F","")))
    high = round(float(screens[room+"thermostat"].labels[5].text.replace(" F","")))
    high = high + 1
    request = 'https://api.idkline.com/thermoset/'+room+'-'+str(low)+'-'+str(high)
    try:
        # switchToScreen("working")
        r =requests.get(request)
        screens[room+"thermostat"].labels[5].text = str(high) + " F"
        screens[room+"thermostat"].draw()
        # time.sleep(3)
    except:
        print('failed to send command: '+request)
    # switchToScreen(room+"thermostat")

def decrease_low_temp(room):
    low = round(float(screens[room+"thermostat"].labels[3].text.replace(" F","")))
    high = round(float(screens[room+"thermostat"].labels[5].text.replace(" F","")))
    low = low - 1
    request = 'https://api.idkline.com/thermoset/'+room+'-'+str(low)+'-'+str(high)
    try:
        # switchToScreen("working")
        r =requests.get(request)
        screens[room+"thermostat"].labels[3].text = str(low) + " F"
        screens[room+"thermostat"].draw()
        # time.sleep(3)
    except:
        print('failed to send command: '+request)
    # switchToScreen(room+"thermostat")

def decrease_high_temp(room):
    low = round(float(screens[room+"thermostat"].labels[3].text.replace(" F","")))
    high = round(float(screens[room+"thermostat"].labels[5].text.replace(" F","")))
    high = high - 1
    request = 'https://api.idkline.com/thermoset/'+room+'-'+str(low)+'-'+str(high)
    try:
        # switchToScreen("working")
        r =requests.get(request)
        screens[room+"thermostat"].labels[5].text = str(high) + " F"
        screens[room+"thermostat"].draw()
        # time.sleep(3)
    except:
        print('failed to send command: '+request)
    # switchToScreen(room+"thermostat")

current_func = ""
current_target = ""
circuits = []
config = {}
status = {}
power = {}
screens = None
modes = ["Morning", "Day", "Lunch", "Day", "Dinner", "Evening", "Shower", "Night", "Dark", "Alert"]
current_mode = "Dark"
current_screen = ""

if __name__ == '__main__':
    window = tk.Tk()
    width = window.winfo_screenwidth()
    height = window.winfo_screenheight()

    window.attributes("-fullscreen", 1)
    window.geometry(str(width)+"x"+str(height))
    #window.geometry("800x500")
    window.configure(bg='black')
    window.columnconfigure(0, minsize=width/3)
    window.columnconfigure(1, minsize=width/3)
    window.columnconfigure(2, minsize=width/3)

    loadConfig()
    switchToScreen("main")

    window.mainloop()