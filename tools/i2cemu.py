import keyboard

last_clock = False
b = ''
while True:
    clock = keyboard.is_pressed('shift')
    data = keyboard.is_pressed('ctrl')

    if last_clock == clock:
        continue

    last_clock = clock

    if clock is not True:
        continue

    bit = 0

    if data is True:
        bit = 1
    
    b = b + str(bit)

    if len(b) == 8:
        byte_val = bytes([int(b, 2)])
        print(f"[{b}] {byte_val}")
        b = ''
    