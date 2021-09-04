import tkinter as tk
import _thread
import time
import RPi.GPIO as GPIO

inner_beam_pin = 20
outer_beam_pin = 21
running = True

inner_beam = 0
outer_beam = 0
direction = "none"
occupants = 0
last_beam_state = "00"
action = ""

def on_beam_state_read(channel):
    global last_beam_state
    global direction
    global inner_beam
    global outer_beam
    a = str(GPIO.input(inner_beam_pin))
    b = str(GPIO.input(outer_beam_pin))
    inner_beam = a
    outer_beam = b
    c = a+b
    if c == last_beam_state:
        return
    if c == "11":
        check_direction()
    elif c == "00":
        direction = "none"
    last_beam_state = c

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

def draw_loop():
    global label1
    global label2
    global label3
    global label4
    last_inner = 0
    last_outer = 0
    last_direction = ""
    last_occupants = 0
    while running is True:
        if inner_beam != last_inner:
            last_inner = inner_beam
            label1.grid_forget()
            label1 = tk.Label(text=str(inner_beam), font = ("Times", 72), bg="black", fg="white")
            label1.grid(row=0, column=0, sticky="nesw", padx=5, pady=5)
        if outer_beam != last_outer:
            last_outer = outer_beam
            label2.grid_forget()
            label2 = tk.Label(text=str(outer_beam), font = ("Times", 72), bg="black", fg="white")
            label2.grid(row=0, column=2, sticky="nesw", padx=5, pady=5)
        if direction != last_direction:
            last_direction = direction
            label3.grid_forget()
            label3 = tk.Label(text=direction, font = ("Times", 64), bg="black", fg="white")
            label3.grid(row=1, column=1, sticky="nesw", padx=5, pady=5)
        if occupants != last_occupants:
            last_occupants = occupants
            label4.grid_forget()
            label4 = tk.Label(text=str(occupants), font = ("Times", 48), bg="black", fg="white")
            label4.grid(row=2, column=1, sticky="nesw", padx=5, pady=5)

def close_click():
    global running
    running = False
    time.sleep(1)
    GPIO.cleanup()
    exit()

GPIO.setmode(GPIO.BCM)
GPIO.setup(inner_beam_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(outer_beam_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(inner_beam_pin, GPIO.BOTH, callback=on_beam_state_read)
GPIO.add_event_detect(outer_beam_pin, GPIO.BOTH, callback=on_beam_state_read)

window = tk.Tk()
label1 = tk.Label(text="0", font = ("Times", 72), bg="black", fg="white")
label2 = tk.Label(text="0", font = ("Times", 72), bg="black", fg="white")
label3 = tk.Label(text="none", font = ("Times", 64), bg="black", fg="white")
label4 = tk.Label(text="0", font = ("Times", 48), bg="black", fg="white")

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

    close_button = tk.Button(text="CLOSE",command=close_click, height=1, font = ("Times", 12), bg="orange", fg="white")
    close_button.grid(row=4, column=1, sticky="nesw", padx=5, pady=5)
        
    _thread.start_new_thread(draw_loop, ())

    window.mainloop()
    