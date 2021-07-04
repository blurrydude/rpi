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
    "grey": "#ededed",
    "darkgrey": "#555555",
    "black": "#000000",
    "white": "#ffffff"
}

def quit():
    exit()

def toggle_coil():
    global coil
    global running
    #TODO: use GPIO to do this thing
    if coil is True:
        coil = False
        main_screen.buttons[0].text.set("Coil Off")
        main_screen.buttons[0].bg = color["blue"]
        main_screen.buttons[1].bg = color["black"]
        main_screen.buttons[1].text.set("Start")
        running = False
    else:
        coil = True
        main_screen.buttons[0].text.set("Coil On")
        main_screen.buttons[0].bg = color["green"]
        main_screen.buttons[1].bg = color["blue"]
    main_screen.clear()
    main_screen.draw()

def start_engine():
    global running
    #TODO: use GPIO to do this thing
    if coil is False or running is True:
        return
    main_screen.buttons[1].bg = color["green"]
    sleep(2)
    #TODO: make sure the engine started before statusing
    main_screen.buttons[1].bg = color["black"]
    main_screen.buttons[1].text.set("Running")
    running = True
    main_screen.clear()
    main_screen.draw()

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

main_screen = Screen()
main_screen.buttons.append(Button("Coil Off",lambda id=0: toggle_coil(),2,("Times",16),color["darkgreen"],color["black"],0,3,6,"nesw",5,5))
main_screen.buttons.append(Button("Start",lambda id=0: start_engine(),2,("Times",16),color["darkgrey"],color["grey"],1,3,6,"nesw",5,5))
main_screen.buttons.append(Button("Exit",lambda id=0: quit(),2,("Times",16),"black",color["grey"],2,3,6,"nesw",5,5))
main_screen.draw()

coil = False
running = False

window.mainloop()