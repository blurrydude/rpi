from new_interface import on_click
import tkinter as tk
from time import sleep

class Button:
    def __init__(self, text, command, height, font, bg, fg, row, col, colspan, sticky, padx, pady):
        self.text = tk.StringVar()
        self.Button = tk.Button(textvariable=self.text,command=command, height=height, font=font, bg=bg, fg=fg)
        self.text.set(text)
        self.height = height
        self.command = command
        self.bg = bg
        self.fg = fg
        self.font = font
        self.row = row
        self.col = col
        self.colspan = colspan
        self.sticky = sticky
        self.padx = padx
        self.pady = pady
    
    def draw(self):
        self.remove()
        self.Button = tk.Button(textvariable=self.text,command=self.command, height=self.height, font=self.font, bg=self.bg, fg=self.fg)
        self.Button.grid(row=self.row, column=self.col, columnspan=self.colspan, sticky=self.sticky, padx=self.padx, pady=self.pady)
    
    def remove(self):
        try:
            self.Button.grid_forget()
        except:
            return

class Label:
    def __init__(self, text, font, bg, fg, row, col, colspan, sticky, padx, pady):
        self.text = tk.StringVar()
        self.Label = tk.Label(textvariable=self.text, font=font, bg=bg, fg=fg)
        self.text.set(text)
        self.font = font
        self.bg = bg
        self.fg = fg
        self.row = row
        self.col = col
        self.colspan = colspan
        self.sticky = sticky
        self.padx = padx
        self.pady = pady
    
    def draw(self):
        self.remove()
        self.Label = tk.Label(textvariable=self.text, font=self.font, bg=self.bg, fg=self.fg)
        self.Label.grid(row=self.row, column=self.col, columnspan=self.colspan, sticky=self.sticky, padx=self.padx, pady=self.pady)
    
    def remove(self):
        try:
            self.Label.grid_forget()
        except:
            return
        
class Screen:
    def __init__(self):
        self.buttons = []
        self.labels = []

    def draw(self):
        for button in self.buttons:
            button.draw()
        for label in self.labels:
            label.draw()

    def clear(self):
        for button in self.buttons:
            button.remove()
        for label in self.labels:
            label.remove()

color = {
    "red": "#aa5555",
    "green": "#55aa55",
    "darkgreen": "#559955",
    "blue": "#5555aa",
    "darkblue": "#555599",
    "grey": "#ededed",
    "darkgrey": "#555555",
    "black": "#000000",
    "white": "#ffffff",
    "orange": "#aaaa55",
    "darkorange": "#999955",
    "purple": "#aa55aa",
    "darkpurple": "#995599",
    "aqua": "#55aaaa",
    "darkaqua": "#559999"
}

def quit():
    exit()

def do_nothing():
    print("doing nothing")

def toggle_light(light_name):
    global light
    global screen
    light[light_name] = light[light_name] == False
    i = 0
    for key in light:
        state = "off"
        c = "darkaqua"
        if light[key] is True:
            state = "on"
            c = "aqua"
        screen["lights"]["buttons"][i].Button.text = key + " " + state
        screen["lights"]["buttons"][i].Button.bg = color[c]
        i = i + 1
    screen["lights"].draw()

def toggle_coil():
    global coil
    global running
    global screen
    global rpm
    #TODO: use GPIO to do this thing
    if coil is True:
        coil = False
        screen["main"].buttons[0].text.set("Coil Off")
        screen["main"].buttons[0].bg = color["blue"]
        screen["main"].buttons[1].bg = color["black"]
        screen["main"].buttons[1].text.set("Start")
        running = False
        rpm = 0
    else:
        coil = True
        screen["main"].buttons[0].text.set("Coil On")
        screen["main"].buttons[0].bg = color["green"]
        screen["main"].buttons[1].bg = color["blue"]
    screen["main"].clear()
    screen["main"].draw()

def start_engine():
    global running
    global rpm
    global screen
    #TODO: use GPIO to do this thing
    if coil is False or running is True:
        return
    screen["main"].buttons[1].bg = color["green"]
    sleep(2)
    #TODO: make sure the engine started before statusing
    rpm = 750
    screen["main"].buttons[1].bg = color["black"]
    screen["main"].buttons[1].text.set("Running")
    running = True
    screen["main"].clear()
    screen["main"].draw()

def navigate_to(screen_name):
    global current_screen
    global screen
    screen[current_screen].clear()
    current_screen = screen_name
    screen[current_screen].draw()

window = tk.Tk()
width = window.winfo_screenwidth()
height = window.winfo_screenheight()
window.configure(bg='black')
window.attributes("-fullscreen", 1)
window.geometry(str(width)+"x"+str(height))
window.columnconfigure(0, minsize=width/12)
window.columnconfigure(1, minsize=width/12)
window.columnconfigure(2, minsize=width/12)
window.columnconfigure(3, minsize=width/12)
window.columnconfigure(4, minsize=width/12)
window.columnconfigure(5, minsize=width/12)
window.columnconfigure(6, minsize=width/12)
window.columnconfigure(7, minsize=width/12)
window.columnconfigure(8, minsize=width/12)
window.columnconfigure(9, minsize=width/12)
window.columnconfigure(10, minsize=width/12)
window.columnconfigure(11, minsize=width/12)

screen = {
    "main": Screen(),
    "ignition": Screen(),
    "sensors": Screen(),
    "lights": Screen(),
    "sound": Screen()
}

light = {
    "head": False,
    "fog": False,
    "road": False,
    "highbeam": False,
    "front_parking": False,
    "rear_parking": False,
    "reverse": False,
    "tail": False,
    "side_marker": False,
    "top_marker": False,
    "bed": False,
    "driver_floor": False,
    "passenger_floor": False,
    "dashboard": False,
    "cab": False,
    "engine": False
}

current_screen = "main"

screen["main"].buttons.append(Button("Ignition",lambda scrn="ignition": navigate_to(scrn),2,("Times",16),color["darkgreen"],color["white"],0,3,6,"nesw",5,5))
screen["main"].buttons.append(Button("Sensors",lambda scrn="sensors": navigate_to(scrn),2,("Times",16),color["darkblue"],color["white"],1,3,6,"nesw",5,5))
screen["main"].buttons.append(Button("Lights",lambda scrn="lights": navigate_to(scrn),2,("Times",16),color["darkaqua"],color["white"],2,3,6,"nesw",5,5))
screen["main"].buttons.append(Button("Sound",lambda scrn="sound": navigate_to(scrn),2,("Times",16),color["darkorange"],color["white"],3,3,6,"nesw",5,5))
screen["main"].labels.append(Label(" ",16,"black","black",4,1,12,"nesw",5,5))
screen["main"].labels.append(Label(" ",16,"black","black",5,1,12,"nesw",5,5))
screen["main"].buttons.append(Button("Exit",lambda id=0: quit(),2,("Times",16),color["red"],color["black"],6,3,6,"nesw",5,5))

screen["ignition"].buttons.append(Button("Coil Off",lambda id=0: toggle_coil(),2,("Times",16),color["darkgreen"],color["black"],0,3,6,"nesw",5,5))
screen["ignition"].buttons.append(Button("Start",lambda id=0: start_engine(),2,("Times",16),color["darkgrey"],color["grey"],1,3,6,"nesw",5,5))
screen["ignition"].labels.append(Label(" ",16,"black","black",2,1,12,"nesw",5,5))
screen["ignition"].labels.append(Label(" ",16,"black","black",3,1,12,"nesw",5,5))
screen["ignition"].buttons.append(Button("Home",lambda scrn="main": navigate_to(scrn),2,("Times",16),color["blue"],color["white"],4,3,6,"nesw",5,5))

screen["sensors"].labels.append(Label(" ",16,"black","black",2,1,12,"nesw",5,5))
screen["sensors"].labels.append(Label(" ",16,"black","black",3,1,12,"nesw",5,5))
screen["sensors"].buttons.append(Button("Home",lambda scrn="main": navigate_to(scrn),2,("Times",16),color["blue"],color["white"],4,3,6,"nesw",5,5))

i = 0
for key in light:
    screen["lights"].buttons.append(Button(key+" off",lambda l=key: toggle_light(l),2,("Times",16),color["darkaqua"],color["white"],i,3,6,"nesw",5,5))
    i = i + 1

screen["lights"].labels.append(Label(" ",16,"black","black",i,1,12,"nesw",5,5))
screen["lights"].labels.append(Label(" ",16,"black","black",i+1,1,12,"nesw",5,5))
screen["lights"].buttons.append(Button("Home",lambda scrn="main": navigate_to(scrn),2,("Times",16),color["blue"],color["white"],i+2,3,6,"nesw",5,5))

screen["sound"].labels.append(Label(" ",16,"black","black",2,1,12,"nesw",5,5))
screen["sound"].labels.append(Label(" ",16,"black","black",3,1,12,"nesw",5,5))
screen["sound"].buttons.append(Button("Home",lambda scrn="main": navigate_to(scrn),2,("Times",16),color["blue"],color["white"],4,3,6,"nesw",5,5))

navigate_to("main")
coil = False
running = False
rpm = 0

window.mainloop()