#! /usr/bin/env python3
import tkinter as tk
import json

class SmartScreen:
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

def switchToScreen(target):
    global current_screen
    print("switchToScreen"+target)
    if current_screen != "":
        screens[current_screen].hide()
    screens[target].draw()
    current_screen = target

def toggleCircuit(target):
    print("toggleCircuit"+target)

def setMode(target):
    print("setMode"+target)

def setZone(target):
    print("setZone"+target)

circuits = []
config = {}
screens = None
modes = ["Morning", "Day", "Lunch", "Day", "Dinner", "Evening", "Shower", "Night", "Dark", "Alert"]
current_mode = "Dark"
current_screen = ""

window = tk.Tk()
width = window.winfo_screenwidth()
height = window.winfo_screenheight()

#window.attributes("-fullscreen", 1)
#window.geometry(str(width)+"x"+str(height))
window.geometry("800x500")
window.configure(bg='black')
window.columnconfigure(0, minsize=266)
window.columnconfigure(1, minsize=266)
window.columnconfigure(2, minsize=266)

loadConfig()
switchToScreen("main")

window.mainloop()