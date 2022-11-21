import neopixel
import board
import time

morse = {
    "a": [1,2],
    "b": [2,1,1,1],
    "c": [2,1,2,1],
    "d": [2,1,1],
    "e": [1],
    "f": [1,1,2,1],
    "g": [2,2,1],
    "h": [1,1,1,1],
    "i": [1,1],
    "j": [1,2,2,2],
    "k": [2,1,2],
    "l": [1,2,1,1],
    "m": [2,2],
    "n": [2,1],
    "o": [2,2,2],
    "p": [1,2,2,1],
    "q": [2,2,1,2],
    "r": [1,2,1],
    "s": [1,1,1],
    "t": [2],
    "u": [1,1,2],
    "v": [1,1,1,2],
    "w": [1,2,2],
    "x": [2,1,1,2],
    "y": [2,1,2,2],
    "z": [2,2,1,1],
    " ": [0],
    "1": [1,2,2,2,2],
    "2": [1,1,2,2,2],
    "3": [1,1,1,2,2],
    "4": [1,1,1,1,2],
    "5": [1,1,1,1,1],
    "6": [2,1,1,1,1],
    "7": [2,2,1,1,1],
    "8": [2,2,2,1,1],
    "9": [2,2,2,2,1],
    "0": [2,2,2,2,2]
}

uot = 0.1
pixel_pin = board.D18
num_pixels = 8
ORDER = neopixel.GRB

pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=1.0, auto_write=False, pixel_order=ORDER
)

def all_on():
    for i in range(8):
        pixels[i] = (128,128,128)
    pixels.show()

def all_off():
    for i in range(8):
        pixels[i] = (0,0,0)
    pixels.show()

def dit():
    all_on()
    time.sleep(uot)
    all_off()
    time.sleep(uot)

def da():
    all_on()
    time.sleep(uot*3)
    all_off()
    time.sleep(uot)

def pause():
    time.sleep(1)

def do_letter(letter):
    l = letter.lower()
    if l not in morse.keys():
        pause()
    code = morse[l]
    for c in code:
        if c == 0:
            pause()
        elif c == 1:
            dit()
        elif c == 2:
            da()
    pause()

def do_message(message):
    for l in message:
        do_letter(l)


if __name__ == "__main__":
    while (True):
        message = input()
        do_message(message)