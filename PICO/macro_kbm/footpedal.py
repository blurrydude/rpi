# SPDX-FileCopyrightText: 2021 John Park for Adafruit Industries
# SPDX-License-Identifier: MIT
# RaspberryPi Pico RP2040 Mechanical Keyboard

import time
import board
from digitalio import DigitalInOut, Direction, Pull
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode
import busio
import displayio
import terminalio
import adafruit_displayio_ssd1306
from adafruit_display_text import label

i2c = busio.I2C (scl=board.GP9, sda=board.GP8) # This RPi Pico way to call I2C
display_bus = displayio.I2CDisplay (i2c, device_address = 0x3C) # The address of my Board
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=64)

def draw(text):
    splash = displayio.Group()

    color_bitmap = displayio.Bitmap(128, 64, 1) # Full screen white
    color_palette = displayio.Palette(1)
    color_palette[0] = 0xFFFFFF  # White

    bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
    splash.append(bg_sprite)

    # Draw a smaller inner rectangle
    inner_bitmap = displayio.Bitmap(118, 54, 1)
    inner_palette = displayio.Palette(1)
    inner_palette[0] = 0x000000  # Black
    inner_sprite = displayio.TileGrid(inner_bitmap, pixel_shader=inner_palette, x=5, y=4)
    splash.append(inner_sprite)
    display.show(splash)

    # Draw a label
    text_area = label.Label(terminalio.FONT, text=text, color=0xFFFF00, x=8, y=15)
    splash.append(text_area)


led = DigitalInOut(board.LED)
led.direction = Direction.OUTPUT
led.value = True

kbd = Keyboard(usb_hid.devices)
cc = ConsumerControl(usb_hid.devices)

def get_keycode(char, with_ctrl, with_alt, with_gui):
    keycodes = []
    if with_ctrl:
        keycodes.append(Keycode.LEFT_CONTROL)
    if with_alt:
        keycodes.append(Keycode.LEFT_ALT)
    if with_gui:
        keycodes.append(Keycode.LEFT_GUI)
    if char == 'a':
        keycodes.append(Keycode.A)
    if char == 'A':
        keycodes.append(Keycode.LEFT_SHIFT)
        keycodes.append(Keycode.A)
    if char == 'b':
        keycodes.append(Keycode.B)
    if char == 'B':
        keycodes.append(Keycode.LEFT_SHIFT)
        keycodes.append(Keycode.B)
    if char == 'c':
        keycodes.append(Keycode.C)
    if char == 'C':
        keycodes.append(Keycode.LEFT_SHIFT)
        keycodes.append(Keycode.C)
    if char == 'd':
        keycodes.append(Keycode.D)
    if char == 'D':
        keycodes.append(Keycode.LEFT_SHIFT)
        keycodes.append(Keycode.D)
    if char == 'e':
        keycodes.append(Keycode.E)
    if char == 'E':
        keycodes.append(Keycode.LEFT_SHIFT)
        keycodes.append(Keycode.E)
    if char == 'f':
        keycodes.append(Keycode.F)
    if char == 'F':
        keycodes.append(Keycode.LEFT_SHIFT)
        keycodes.append(Keycode.F)
    if char == 'g':
        keycodes.append(Keycode.G)
    if char == 'G':
        keycodes.append(Keycode.LEFT_SHIFT)
        keycodes.append(Keycode.G)
    if char == 'h':
        keycodes.append(Keycode.H)
    if char == 'H':
        keycodes.append(Keycode.LEFT_SHIFT)
        keycodes.append(Keycode.H)
    if char == 'i':
        keycodes.append(Keycode.I)
    if char == 'I':
        keycodes.append(Keycode.LEFT_SHIFT)
        keycodes.append(Keycode.I)
    if char == 'j':
        keycodes.append(Keycode.J)
    if char == 'J':
        keycodes.append(Keycode.LEFT_SHIFT)
        keycodes.append(Keycode.J)
    if char == 'k':
        keycodes.append(Keycode.K)
    if char == 'K':
        keycodes.append(Keycode.LEFT_SHIFT)
        keycodes.append(Keycode.K)
    if char == 'l':
        keycodes.append(Keycode.L)
    if char == 'L':
        keycodes.append(Keycode.LEFT_SHIFT)
        keycodes.append(Keycode.L)
    if char == 'm':
        keycodes.append(Keycode.M)
    if char == 'M':
        keycodes.append(Keycode.LEFT_SHIFT)
        keycodes.append(Keycode.M)
    if char == 'n':
        keycodes.append(Keycode.N)
    if char == 'N':
        keycodes.append(Keycode.LEFT_SHIFT)
        keycodes.append(Keycode.N)
    if char == 'o':
        keycodes.append(Keycode.O)
    if char == 'O':
        keycodes.append(Keycode.LEFT_SHIFT)
        keycodes.append(Keycode.O)
    if char == 'p':
        keycodes.append(Keycode.P)
    if char == 'P':
        keycodes.append(Keycode.LEFT_SHIFT)
        keycodes.append(Keycode.P)
    if char == 'q':
        keycodes.append(Keycode.Q)
    if char == 'Q':
        keycodes.append(Keycode.LEFT_SHIFT)
        keycodes.append(Keycode.Q)
    if char == 'r':
        keycodes.append(Keycode.R)
    if char == 'R':
        keycodes.append(Keycode.LEFT_SHIFT)
        keycodes.append(Keycode.R)
    if char == 's':
        keycodes.append(Keycode.S)
    if char == 'S':
        keycodes.append(Keycode.LEFT_SHIFT)
        keycodes.append(Keycode.S)
    if char == 't':
        keycodes.append(Keycode.T)
    if char == 'T':
        keycodes.append(Keycode.LEFT_SHIFT)
        keycodes.append(Keycode.T)
    if char == 'u':
        keycodes.append(Keycode.U)
    if char == 'U':
        keycodes.append(Keycode.LEFT_SHIFT)
        keycodes.append(Keycode.U)
    if char == 'v':
        keycodes.append(Keycode.V)
    if char == 'V':
        keycodes.append(Keycode.LEFT_SHIFT)
        keycodes.append(Keycode.V)
    if char == 'w':
        keycodes.append(Keycode.W)
    if char == 'W':
        keycodes.append(Keycode.LEFT_SHIFT)
        keycodes.append(Keycode.W)
    if char == 'x':
        keycodes.append(Keycode.X)
    if char == 'X':
        keycodes.append(Keycode.LEFT_SHIFT)
        keycodes.append(Keycode.X)
    if char == 'y':
        keycodes.append(Keycode.Y)
    if char == 'Y':
        keycodes.append(Keycode.LEFT_SHIFT)
        keycodes.append(Keycode.Y)
    if char == 'z':
        keycodes.append(Keycode.Z)
    if char == 'Z':
        keycodes.append(Keycode.LEFT_SHIFT)
        keycodes.append(Keycode.Z)
    if char == ' ':
        keycodes.append(Keycode.SPACE)
    if char == '.':
        keycodes.append(Keycode.PERIOD)
    if char == ',':
        keycodes.append(Keycode.COMMA)
    if char == '`':
        keycodes.append(Keycode.TAB)
    return keycodes

macros = [
    '^C',
    '^V',
    '^x',
    '^z',
    '^t',
    '~`',
    '^~t',
    'play/pause',
    'next',
    'prev',
    'mute',
    'quieter',
    'louder',
    'dimmer',
    'brighter'
]

macro_pedal_A = 0
macro_pedal_B = 1
macro_pedal_C = 2

def show_macros():
    macro_a = macros[macro_pedal_A]
    macro_b = macros[macro_pedal_B]
    macro_c = macros[macro_pedal_C]
    swapem = [
        ('^','CTRL+'),
        ('`','TAB'),
        ('~','ALT+'),
        ('#','GUI+'),
        ('\\CTRL+','^'),
        ('\\ALT+','~'),
        ('\\GUI+','#')
    ]
    for swap in swapem:
        macro_a = macro_a.replace(swap[0],swap[1])
        macro_b = macro_b.replace(swap[0],swap[1])
        macro_c = macro_c.replace(swap[0],swap[1])
    draw(f"A: {macro_a}\nB: {macro_b}\nC: {macro_c}")

def cycle_macro_pedals():
    global macro_pedal_A
    global macro_pedal_B
    global macro_pedal_C
    macro_pedal_A = macro_pedal_A + 1
    lim = len(macros)
    if macro_pedal_A == lim:
        macro_pedal_A = 0
    macro_pedal_B = macro_pedal_A + 1
    if macro_pedal_B == lim:
        macro_pedal_B = 0
    macro_pedal_C = macro_pedal_B + 1
    if macro_pedal_C == lim:
        macro_pedal_C = 0
    show_macros()


def run_macro(macro):
    if macro == 'play/pause':
        cc.send(ConsumerControlCode.PLAY_PAUSE)
        return
    if macro == 'next':
        cc.send(ConsumerControlCode.SCAN_NEXT_TRACK)
        return
    if macro == 'prev':
        cc.send(ConsumerControlCode.SCAN_PREVIOUS_TRACK)
        return
    if macro == 'mute':
        cc.send(ConsumerControlCode.MUTE)
        return
    if macro == 'quieter':
        cc.send(ConsumerControlCode.VOLUME_DECREMENT)
        return
    if macro == 'louder':
        cc.send(ConsumerControlCode.VOLUME_INCREMENT)
        return
    if macro == 'dimmer':
        cc.send(ConsumerControlCode.BRIGHTNESS_DECREMENT)
        return
    if macro == 'brighter':
        cc.send(ConsumerControlCode.BRIGHTNESS_INCREMENT)
        return

    with_ctrl = False
    with_alt = False
    with_gui = False
    escape = False
    for c in macro:
        if c == '\\':
            escape = True
            continue
        if escape is not True:
            if c == '^':
                with_ctrl = True
                continue
            if c == '~':
                with_alt = True
                continue
            if c == '#':
                with_gui = True
                continue
        else:
            escape = False
        kc = get_keycode(c, with_ctrl, with_alt, with_gui)
        if kc is None:
            continue
        kbd.press(*kc)
        time.sleep(0.01)
        kbd.release(*kc)
        time.sleep(0.01)
        with_ctrl = False
        with_alt = False
        with_gui = False

last_state = 0
last_state_2 = 0
last_state_3 = 0
last_state_4 = 0

switch = DigitalInOut(board.GP10)
switch.direction = Direction.INPUT
switch.pull = Pull.UP

switch_2 = DigitalInOut(board.GP11)
switch_2.direction = Direction.INPUT
switch_2.pull = Pull.UP

switch_3 = DigitalInOut(board.GP13)
switch_3.direction = Direction.INPUT
switch_3.pull = Pull.UP

switch_4 = DigitalInOut(board.GP12)
switch_4.direction = Direction.INPUT
switch_4.pull = Pull.UP

show_macros()

while True:
    state = switch.value
    state_2 = switch_2.value
    state_3 = switch_3.value
    state_4 = switch_4.value
    if last_state != state:
        last_state = state
        if state == 0:
            run_macro(macros[macro_pedal_A])
    if last_state_2 != state_2:
        last_state_2 = state_2
        if state_2 == 0:
            run_macro(macros[macro_pedal_B])
    if last_state_3 != state_3:
        last_state_3 = state_3
        if state_3 == 0:
            run_macro(macros[macro_pedal_C])
    if last_state_4 != state_4:
        last_state_4 = state_4
        if state_4 == 0:
            cycle_macro_pedals()
    time.sleep(0.01)  # debounce


# # list of pins to use (skipping GP15 on Pico because it's funky)
# pins = (
#     board.GP0,
#     board.GP1,
#     board.GP2,
#     board.GP3,
#     board.GP4,
#     board.GP5,
#     board.GP6,
#     board.GP7,
#     board.GP10,
#     board.GP11,
#     board.GP12,
#     board.GP13,
#     board.GP14,
#     board.GP16,
#     board.GP17,
#     board.GP18,
#     board.GP19,
#     board.GP20,
#     board.GP21,
# )

# MEDIA = 1
# KEY = 2

# keymap = {
#     (0): (KEY, (Keycode.GUI, Keycode.C)),
#     (1): (KEY, (Keycode.GUI, Keycode.V)),
#     (2): (KEY, [Keycode.THREE]),
#     (3): (KEY, [Keycode.FOUR]),
#     (4): (KEY, [Keycode.FIVE]),
#     (5): (MEDIA, ConsumerControlCode.VOLUME_DECREMENT),
#     (6): (MEDIA, ConsumerControlCode.VOLUME_INCREMENT),

#     (7): (KEY, [Keycode.R]),

#     (8): (MEDIA, ConsumerControlCode.PLAY_PAUSE),
#     (9): (MEDIA, ConsumerControlCode.VOLUME_DECREMENT),
#     (10): (MEDIA, ConsumerControlCode.VOLUME_INCREMENT),
#     (11): (MEDIA, ConsumerControlCode.MUTE),
#     (12): (KEY, (Keycode.LEFT_ALT, Keycode.TAB)),
    
#     (13): (KEY, [Keycode.O]),
#     (14): (KEY, [Keycode.LEFT_ARROW]),
#     (15): (KEY, [Keycode.DOWN_ARROW]),
#     (16): (KEY, [Keycode.RIGHT_ARROW]),
#     (17): (KEY, [Keycode.ALT]),
#     (18): (KEY, [Keycode.U]),

# }

# switches = []
# for i in range(len(pins)):
#     switch = DigitalInOut(pins[i])
#     switch.direction = Direction.INPUT
#     switch.pull = Pull.UP
#     switches.append(switch)


# switch_state = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

# while True:
#     for button in range(19):
#         if switch_state[button] == 0:
#             if not switches[button].value:
#                 try:
#                     if keymap[button][0] == KEY:
#                         kbd.press(*keymap[button][1])
#                     else:
#                         cc.send(keymap[button][1])
#                     draw(f"{keymap[button][1]}")
#                 except ValueError:  # deals w six key limit
#                     pass
#                 switch_state[button] = 1

#         if switch_state[button] == 1:
#             if switches[button].value:
#                 try:
#                     if keymap[button][0] == KEY:
#                         kbd.release(*keymap[button][1])

#                 except ValueError:
#                     pass
#                 switch_state[button] = 0

#     time.sleep(0.01)  # debounce