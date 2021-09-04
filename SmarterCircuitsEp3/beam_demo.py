import tkinter as tk
import _thread
import time

inner_beam = 0
outer_beam = 0
direction = "none"
occupants = 0
last_beam_state = "00"
action = ""

window = tk.Tk()
label1 = tk.Label(text="0", font = ("Times", 72), bg="black", fg="white")
label2 = tk.Label(text="0", font = ("Times", 72), bg="black", fg="white")
label3 = tk.Label(text="none", font = ("Times", 64), bg="black", fg="white")
label4 = tk.Label(text="0", font = ("Times", 48), bg="black", fg="white")
label5 = tk.Label(text="", font = ("Times", 48), bg="black", fg="white")

def on_beam_state_read():
    global last_beam_state
    global direction
    a = str(inner_beam)
    b = str(outer_beam)
    c = a+b
    if c == last_beam_state:
        return
    if c == "11":
        check_direction()
    elif c == "00":
        direction = "none"
    last_beam_state = c
    draw_labels()

def check_direction():
    global direction
    global occupants
    if last_beam_state == "01":
        direction = "out"
        if occupants > 0:
            occupants = occupants - 1
    if last_beam_state == "10":
        direction = "in"
        occupants = occupants + 1

def draw_labels():
    global label1
    global label2
    global label3
    global label4
    label1.grid_forget()
    label2.grid_forget()
    label3.grid_forget()
    label4.grid_forget()
    label1 = tk.Label(text=str(inner_beam), font = ("Times", 72), bg="black", fg="white")
    label2 = tk.Label(text=str(outer_beam), font = ("Times", 72), bg="black", fg="white")
    label3 = tk.Label(text=direction, font = ("Times", 64), bg="black", fg="white")
    label4 = tk.Label(text=str(occupants), font = ("Times", 48), bg="black", fg="white")
    label5 = tk.Label(text=action, font = ("Times", 48), bg="black", fg="white")
    label1.grid(row=0, column=0, sticky="nesw", padx=5, pady=5)
    label2.grid(row=0, column=2, sticky="nesw", padx=5, pady=5)
    label3.grid(row=1, column=1, sticky="nesw", padx=5, pady=5)
    label4.grid(row=2, column=1, sticky="nesw", padx=5, pady=5)
    label5.grid(row=3, column=1, sticky="nesw", padx=5, pady=5)

def close_click():
    exit()

def demo():
    global inner_beam
    global outer_beam
    global action
    time.sleep(3)
    demo_enter()
    time.sleep(2)
    demo_enter()
    time.sleep(2)
    demo_exit()
    time.sleep(2)
    demo_play_with_door()
    time.sleep(2)
    demo_enter()
    time.sleep(2)
    demo_exit()
    time.sleep(2)
    demo_enter()
    time.sleep(2)
    demo_play_with_door()
    time.sleep(2)
    demo_enter()
    time.sleep(2)

def demo_enter():
    global action
    action = "open door"
    demo_door()
    action = "walk in"
    demo_in()
    action = "close door"
    demo_door()
    action = ""
    draw_labels()

def demo_exit():
    global action
    action = "open door"
    demo_door()
    action = "walk out"
    demo_out()
    action = "close door"
    demo_door()
    action = ""
    draw_labels()

def demo_play_with_door():
    global action
    action = "open door"
    demo_door()
    action = "close door"
    demo_door()
    action = ""
    draw_labels()

def demo_out():
    global inner_beam
    global outer_beam
    on_beam_state_read()
    time.sleep(1)
    inner_beam = 0
    outer_beam = 1
    on_beam_state_read()
    time.sleep(1)
    inner_beam = 1
    outer_beam = 1
    on_beam_state_read()
    time.sleep(1)
    inner_beam = 1
    outer_beam = 0
    on_beam_state_read()
    time.sleep(1)
    inner_beam = 0
    outer_beam = 0
    on_beam_state_read()
    time.sleep(1)
    
def demo_in():
    global inner_beam
    global outer_beam
    on_beam_state_read()
    time.sleep(1)
    inner_beam = 1
    outer_beam = 0
    on_beam_state_read()
    time.sleep(1)
    inner_beam = 1
    outer_beam = 1
    on_beam_state_read()
    time.sleep(1)
    inner_beam = 0
    outer_beam = 1
    on_beam_state_read()
    time.sleep(1)
    inner_beam = 0
    outer_beam = 0
    on_beam_state_read()
    time.sleep(1)
    
def demo_door():
    global inner_beam
    global outer_beam
    on_beam_state_read()
    time.sleep(1)
    inner_beam = 1
    outer_beam = 0
    on_beam_state_read()
    time.sleep(1)
    inner_beam = 0
    outer_beam = 0
    on_beam_state_read()
    time.sleep(1)

if __name__ == '__main__':
    width = window.winfo_screenwidth()
    height = window.winfo_screenheight()

    window.attributes("-fullscreen", 1)
    window.geometry(str(width)+"x"+str(height))
    window.configure(bg='black')
    window.columnconfigure(0, minsize=width/3)
    window.columnconfigure(1, minsize=width/3)
    window.columnconfigure(2, minsize=width/3)

    label1.grid(row=0, column=0, sticky="nesw", padx=5, pady=5)
    label2.grid(row=0, column=2, sticky="nesw", padx=5, pady=5)
    label3.grid(row=1, column=1, sticky="nesw", padx=5, pady=5)
    label4.grid(row=2, column=1, sticky="nesw", padx=5, pady=5)
    label5.grid(row=3, column=1, sticky="nesw", padx=5, pady=5)

    close_button = tk.Button(text="CLOSE",command=close_click, height=1, font = ("Times", 12), bg="orange", fg="white")
    close_button.grid(row=4, column=1, sticky="nesw", padx=5, pady=5)

    _thread.start_new_thread(demo, ())
    window.mainloop()