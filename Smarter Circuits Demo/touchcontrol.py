import time
import tkinter as tk
import requests
import json

my_circuit = "Reading Light"
relay = "0"

def on_click():
    send_command(my_circuit+" on")

def off_click():
    send_command(my_circuit+" off")

def close_click():
    exit()

def send_command(command):
    try:
        r =requests.get('http://192.168.0.8:8080/control/'+command)
    except:
        print('failed to send command')

def get_state():
    global state
    r = requests.get('http://192.168.0.8:8080/states')
    states = json.loads(r.text)
    circuit = my_circuit.lower().replace(" ","_")
    if circuit not in states.keys():
        return "Unknown Circuit"
    if "relay_"+relay not in states[circuit].keys():
        return "Unknown State"
    return states[circuit]["relay_"+relay]

if __name__ == '__main__':
    window = tk.Tk()
    width = window.winfo_screenwidth()
    height = window.winfo_screenheight()

    window.attributes("-fullscreen", 1)
    window.geometry(str(width)+"x"+str(height))
    window.configure(bg='black')
    window.columnconfigure(0, minsize=width/3)
    window.columnconfigure(1, minsize=width/3)
    window.columnconfigure(2, minsize=width/3)

    label = tk.Label(text=my_circuit, font = ("Times", 20), bg="black", fg="white")
    label.grid(row=0, column=1, sticky="nesw", padx=5, pady=5)

    on_button = tk.Button(text="ON",command=on_click, height=3, font = ("Times", 16), bg="darkgreen", fg="white")
    on_button.grid(row=1, column=1, sticky="nesw", padx=5, pady=5)

    off_button = tk.Button(text="OFF",command=off_click, height=3, font = ("Times", 16), bg="darkred", fg="white")
    off_button.grid(row=2, column=1, sticky="nesw", padx=5, pady=5)

    off_button = tk.Button(text="CLOSE",command=close_click, height=1, font = ("Times", 12), bg="orange", fg="white")
    off_button.grid(row=3, column=2, sticky="nesw", padx=5, pady=5)

    window.mainloop()