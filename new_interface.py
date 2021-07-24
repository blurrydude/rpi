#! /usr/bin/env python3
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
        print(button.text)
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
    toggle_screen = SmartScreen()
    toggle_screen.buttons.append(SmartButton(toggle_screen, {
                "text": "Cancel", "func": "screen", "target":"main",
                "height": 2, "fontname": "Times", "fontsize": 20,
                "bg": "orange", "fg": "white", "sticky": "nesw",
                "row": 0, "col": 1, "padx": 5, "pady": 5
            }))
    toggle_screen.buttons.append(SmartButton(toggle_screen, {
                "text": "ON", "func": "toggleon", "target":"",
                "height": 4, "fontname": "Times", "fontsize": 20,
                "bg": "darkgreen", "fg": "white", "sticky": "nesw",
                "row": 1, "col": 1, "padx": 5, "pady": 5
            }))
    toggle_screen.buttons.append(SmartButton(toggle_screen, {
                "text": "OFF", "func": "toggleoff", "target":"",
                "height": 4, "fontname": "Times", "fontsize": 20,
                "bg": "darkred", "fg": "white", "sticky": "nesw",
                "row": 2, "col": 1, "padx": 5, "pady": 5
            }))
    screens["toggle"] = toggle_screen

def switchToScreen(target):
    global current_screen
    print("switchToScreen "+target)
    if current_screen != "":
        screens[current_screen].hide()
    screens[target].draw()
    current_screen = target

def toggleCircuit(target):
    global current_func
    global current_target
    print("toggleCircuit "+target)
    current_func = "circuit"
    current_target = target
    switchToScreen("toggle")

def setMode(target):
    print("setMode "+target)
    sendCommand('set mode '+target)

def setZone(target):
    global current_func
    global current_target
    print("setZone "+target)
    current_func = "zone"
    current_target = target
    switchToScreen("toggle")

def sendCommand(command):
    print("sending command: "+command)
    r =requests.get('https://api.idkline.com/control/'+command)
    print(str(r.status_code))
    switchToScreen("main")

current_func = ""
current_target = ""
circuits = []
config = {}
screens = None
modes = ["Morning", "Day", "Lunch", "Day", "Dinner", "Evening", "Shower", "Night", "Dark", "Alert"]
current_mode = "Dark"
current_screen = ""

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