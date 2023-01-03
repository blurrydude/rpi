from machine import Pin, PWM
from picozero import LED
import time
import random
#import neopixel
#import machine
#pixels = neopixel.NeoPixel(machine.Pin(1),8)
#pixels.brightness = 0.5
led = LED(25)
buzzer = PWM(Pin(15))
# notes = [        
#         130.81,
#         #138.59,
#         146.83,
#         #155.56,
#         164.81,
#         174.61,
#         #185.00,
#         196.00,
#         #207.65,
#         220.00,
#         #233.08,
#         246.94,
#         261.63
#     ]
notes = [
    33,  # C   0
    35,  # C#  1
    37,  # D   2
    39,  # D#  3
    41,  # E   4
    44,  # F   5
    46,  # F#  6
    49,  # G   7
    52,  # G#  8
    55,  # A   9
    58,  # A# 10
    62,  # B  11
    65,  # C  12
    69,  # C# 13
    73,  # D  14
    78,  # D# 15
    82,  # E  16
    87,  # F  17
    93,  # F# 18
    98,  # G  19
    104, # G# 20
    110, # A  21
    117, # A# 22
    123, # B  23
    131, # C  24
    139, # C# 25
    147, # D  26
    156, # D# 27
    165, # E  28
    175, # F  29
    185, # F# 30
    196, # G  31
    208, # G# 32
    220, # A  33
    233, # A# 34
    247, # B  35
    262, # C  36
    277, # C# 37
    294, # D  38
    311, # D# 39
    330, # E  40
    349, # F  41
    370, # F# 42
    392, # G  43
    415, # G# 44
    440, # A  45
    466, # A# 46
    494, # B  47
    523, # C  48
    554, # C# 49
    587, # D  50
    622, # D# 51
    659, # E  52
    698, # F  53
    734, # F# 54
    784, # G  55
    831, # G# 56
    880, # A  57
    932, # A# 58
    988  # B  59
    ]

def note(n):
    return notes[note_index(n)]

def note_index(n):
    if n == 'c':
        return 0
    if n == 'c#':
        return 1
    if n == 'd':
        return 2
    if n == 'd#':
        return 3
    if n == 'e':
        return 4
    if n == 'f':
        return 5
    if n == 'f#':
        return 6
    if n == 'g':
        return 7
    if n == 'g#':
        return 8
    if n == 'a':
        return 9
    if n == 'a#':
        return 10
    if n == 'b':
        return 11
    if n == 'c2':
        return 12
    if n == 'c2#':
        return 13
    if n == 'd2':
        return 14
    if n == 'd2#':
        return 15
    if n == 'e2':
        return 16
    if n == 'f2':
        return 17
    if n == 'f2#':
        return 18
    if n == 'g2':
        return 19
    if n == 'g2#':
        return 20
    if n == 'a2':
        return 21
    if n == 'a2#':
        return 22
    if n == 'b2':
        return 23
    if n == 'c3':
        return 24
    if n == 'c3#':
        return 25
    if n == 'd3':
        return 26
    if n == 'd3#':
        return 27
    if n == 'e3':
        return 28
    if n == 'f3':
        return 29
    if n == 'f3#':
        return 30
    if n == 'g3':
        return 31
    if n == 'g3#':
        return 32
    if n == 'a3':
        return 33
    if n == 'a3#':
        return 34
    if n == 'b3':
        return 35
    if n == 'c4':
        return 36
    if n == 'c4#':
        return 37
    if n == 'd4':
        return 38
    if n == 'd4#':
        return 39
    if n == 'e4':
        return 40
    if n == 'f4':
        return 41
    if n == 'f4#':
        return 42
    if n == 'g4':
        return 43
    if n == 'g4#':
        return 44
    if n == 'a4':
        return 45
    if n == 'a4#':
        return 46
    if n == 'b4':
        return 47
    if n == 'c5':
        return 48
    if n == 'c5#':
        return 49
    if n == 'd5':
        return 50
    if n == 'd5#':
        return 51
    if n == 'e5':
        return 52
    if n == 'f5':
        return 53
    if n == 'f5#':
        return 54
    if n == 'g5':
        return 55
    if n == 'g5#':
        return 56
    if n == 'a5':
        return 57
    if n == 'a5#':
        return 58
    if n == 'b5':
        return 59
    return 59
    

def play_note(n, dur):
    play_tone(notes[note(n)])
    time.sleep(dur)
    be_quiet()
    
def play_note_id(i, dur):
    play_tone(notes[i])
    time.sleep(dur)
    be_quiet()

def arpeggio(root, steps, dur = 0.15, delay = 0.1):
    for i in range(root, root+steps):
        play_tone(notes[i])
        time.sleep(dur)
        be_quiet()
        time.sleep(delay)

def sweep_up(fro = 80, steps = 8, decay = 0.0025, step_size = 24, step_dur = 0.05):
    buzzer.duty_u16(1000)
    for i in range(steps):
        buzzer.freq(fro+(i*step_size))
        time.sleep(step_dur-(i*decay))
    be_quiet()

def sweep_down(fro = 110, steps = 8, decay = 0.0025, step_size = 12, step_dur = 0.05):
    buzzer.duty_u16(1000)
    for i in range(steps):
        buzzer.freq(fro-(i*step_size))
        time.sleep(step_dur-(i*decay))
    be_quiet()
    

def play_tone(frequency):
    # Set maximum volume
    buzzer.duty_u16(1000)
    # Play tone
    buzzer.freq(round(frequency))

def be_quiet():
    # Set minimum volume
    buzzer.duty_u16(0)
    
def whoa():
    sweep_up(80)
    sweep_down(110)

def grumble():
    play_tone(150)
    time.sleep(0.05)
    play_tone(90)
    time.sleep(0.3)
    be_quiet()

def complain():
    play_tone(39)
    time.sleep(0.15)
    be_quiet()
    time.sleep(0.1)
    play_tone(46)
    time.sleep(0.35)
    be_quiet()
    time.sleep(0.1)
    play_tone(37)
    time.sleep(0.25)
    be_quiet()
    time.sleep(0.1)
    play_tone(41)
    time.sleep(0.35)
    be_quiet()
    time.sleep(0.1)
    play_tone(41)
    time.sleep(0.35)
    be_quiet()

def alert():
    sweep_up(fro=60, steps=32, decay=0, step_size=24, step_dur=0.02)

def big_alert():
    alert()
    time.sleep(0.5)
    alert()
    time.sleep(0.5)
    alert()
    time.sleep(0.5)
    
def play_music(music):
    beat = 0.1
    current_note = ''
    start_note = True
    sustain = True
    for c in music:
        try:
            #print(c)
            if c == '-' and start_note is True:
                #print('play_tone '+current_note)
                play_tone(note(current_note))
                start_note = False
                sustain = True
            elif c == '-' and start_note is False:
                #print('beat')
                time.sleep(beat)
            elif c == '_':
                #print('be_quiet')
                be_quiet()
                start_note = False
            elif sustain is True:
                sustain = False
                #print('stop_note')
                current_note = ''
                #print('build current_note')
                current_note = current_note + c
            else:
                #print('build current_note')
                current_note = current_note + c
                start_note = True
        except:
            print('bad at '+c)
            be_quiet()
    be_quiet()

def startup():    
    music = "c2--_--e2--_--f2#------"
    #pixels.fill((255,255,255))
    play_music(music)
    time.sleep(2)


def think():
    think_time = random.randint(10, 42)
    print('thinking '+str(think_time))
    now = 0
    led_on = False
    while now < think_time:
        now = now + 1
        delay = random.randint(1,5)
        n = random.randint(0,len(notes)-1)
        #letter = random.randint(0,4)
        if led_on is False:
            play_note_id(n,delay*0.02)
            led_on = True
        else:
            be_quiet()
            led_on = False
        time.sleep(delay*0.05)
    be_quiet()
    
#pixels.fill((255,0,0))
#grumble()
#complain()
#pixels.fill((0,0,0))
#time.sleep(1)
#arpeggio(16,16, dur=0.05, delay=0.02)
def tetris(): #Korobeiniki
    play_music("e5----_-b4--_-c5--_-d5--e5--d5--_-c5--_-b4--_-a4----_-a4--_-c5--_-e5----_-d5---_-c5--_-b4----_-b4--_-c5--_-d5----_-e5----_-c5----_-a4----_-a4----_")
    play_music("_--d5-----_-d5--_-f5--_-a5----_-g5--_-f5--_-e5----_-c5--_-e5----_-d5--_-c5--_-b4----_-b4--_-b4--_c5--_-d5----_-e5----_-c5----_-a4----_-a4------_")

while True:
    think()
    mood = random.randint(0, 30)
    print('mood '+str(mood))
    if mood < 10:
        grumble()
    if mood < 5:
        complain()
    if mood > 28: 
        #play_music("c2--_--e2--_--e2--_--f2--_--f2--_--g2--_--a2--_--b2----g2--_--a2--_--a2--_--b2--_--b2--_--c3----b2---_--_")
        tetris()
    elif mood > 25:
        #play_music("a2--_--a2--_-a2----_-a5--------_")
        whoa()
    think_delay = random.randint(5, 120)
    print('waiting '+str(think_delay))
    for i in range(think_delay):
        print(str(think_delay-i))
        time.sleep(1)
