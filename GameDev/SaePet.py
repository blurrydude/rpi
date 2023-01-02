from machine import Pin, PWM
from picozero import LED
import time
import random

led = LED(25)
buzzer = PWM(Pin(15))
l = [LED(5)]
on_light = 0

button_1 = Pin(6, Pin.IN)
button_2 = Pin(7, Pin.IN)
button_3 = Pin(8, Pin.IN)
button_4 = Pin(9, Pin.IN)
b1_pressed = False
b2_pressed = False
b3_pressed = False
b4_pressed = False
think_delay = 0
game_state = None

for i in range(5):
    l.append(LED(i))

mood = 0
energy = 100
sleeping = False
playing = False
playing_match = False

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
note_names = ['c','c#','d','d#','e','f','f#','g','g#','a','a#','b','c2','c2#','d2','d2#','e2','f2','f2#','g2','g2#','a2','a2#','b2','c3','c3#','d3','d3#','e3','f3','f3#','g3','g3#','a3','a3#','b3','c4','c4#','d4','d4#','e4','f4','f4#','g4','g4#','a4','a4#','b4','c5','c5#','d5','d5#','e5','f5','f5#','g5','g5#','a5','a5#','b5', ]

def use_energy():
    global energy
    energy = energy - 1
    if energy < 0:
        energy = 0

def gooden_mood():
    global mood
    mood = mood + 1
    if mood > 10:
        mood = 10

def badden_mood():
    global mood
    mood = mood - 1
    if mood < -10:
        mood = -10

def rest():
    print('resting')
    global energy
    global mood
    global sleeping
    sleeping = True
    i = 1
    while energy < 100:
        chance = random.randint(1,10)
        if chance > 9:
            energy = energy + 2
            arpeggio(9,8, dur = 0.05, delay = 0.05)
            sweep_down(160)
        else:
            energy = energy + 1
        l[i].on()
        time.sleep(0.5)
        l[i].off()
        i = i + 1
        if i == 6:
            i = 1
        print('energy '+str(energy))
    sleeping = False

def note(n):
    return notes[note_index(n)]

def note_index(n):
    #print('get note index for '+n)
    return note_names.index(n)

def play_note(n, dur):
    play_tone(note(n),True)
    li = (note_index(n)%5)+1
    l[li].on()
    time.sleep(dur)
    l[li].off()
    be_quiet()
    
def play_note_id(i, dur):
    play_tone(notes[i],True)
    li = (i%5)+1
    l[li].on()
    time.sleep(dur)
    l[li].off()
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
        li = (i%5)+1
        l[li].on()
        buzzer.freq(fro+(i*step_size))
        time.sleep(step_dur-(i*decay))
        l[li].off()
    be_quiet()

def sweep_down(fro = 110, steps = 8, decay = 0.0025, step_size = 12, step_dur = 0.05):
    buzzer.duty_u16(1000)
    for i in range(steps):
        li = (i%5)+1
        l[li].on()
        buzzer.freq(fro-(i*step_size))
        time.sleep(step_dur-(i*decay))
        l[li].off()
    be_quiet()

def play_tone(frequency, bypass_led = False):
    global on_light
    # Set maximum volume
    buzzer.duty_u16(1000)
    # Play tone
    buzzer.freq(round(frequency))
    if bypass_led is False:
        on_light = (frequency%5)+1
        l[on_light].on()
    use_energy()

def be_quiet():
    # Set minimum volume
    buzzer.duty_u16(0)
    l[on_light].off()

def break_block():
    l[0].on()
    time.sleep(0.05)
    l[0].off()
    time.sleep(0.15)
    for i in range(5):
        l[i+1].on()
        time.sleep(0.1)
        l[i+1].off()
    use_energy()

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
                play_tone(note(current_note),True)
                li = (note_index(current_note)%5)+1
                l[li].on()
                start_note = False
                sustain = True
            elif c == '-' and start_note is False:
                #print('beat')
                time.sleep(beat)
            elif c == '_':
                #print('be_quiet')
                be_quiet()
                li = (note_index(current_note)%5)+1
                l[li].off()
                start_note = False
            elif sustain is True:
                sustain = False
                #print('stop_note')
                try:
                    li = (note_index(current_note)%5)+1
                    l[li].off()
                except:
                    pass
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
    global mood
    
    think_time = random.randint(10, 42)
    print('thinking '+str(think_time))
    now = 0
    led_on = False
    while now < think_time:
        now = now + 1
        delay = random.randint(1,8)
        n = random.randint(0,len(notes)-1)
        h = len(notes)*0.25
        tq = len(notes)*0.75
        if n < h:
            badden_mood()
        elif n > tq:
            gooden_mood()
        #letter = random.randint(0,4)
        if led_on is False:
            play_note_id(n,delay*0.02)
            led_on = True
        else:
            be_quiet()
            led_on = False
        time.sleep(delay*0.05)
    be_quiet()

def older():
    play_music("c2--_--e2--_--e2--_--f2--_--f2--_--g2--_--a2--_--b2----g2--_--a2--_--a2--_--b2--_--b2--_--c3----b2---_--_--e2--_--g2--_--g2--_--a2--_--a2--_--b2----a2---_--_--d2--_--f2--_--f2--_--g2--_--g2--_--a2----g2---_--_")

def tetris(): #Korobeiniki
    play_music("e5----_-b4--_-c5--_-d5--e5--d5--_-c5--_-b4--_-a4----_-a4--_-c5--_-e5----_-d5---_-c5--_-b4----_-b4--_-c5--_-d5----_-e5----_-c5----_-a4----_-a4----_")
    play_music("_--d5-----_-d5--_-f5--_-a5----_-g5--_-f5--_-e5----_-c5--_-e5----_-d5--_-c5--_-b4----_-b4--_-b4--_c5--_-d5----_-e5----_-c5----_-a4----_-a4------_")

def run_original():
    while True:
        think()
        mood = random.randint(0, 30)
        print('mood '+str(mood))
        if mood < 10:
            grumble()
        if mood < 5:
            complain()
        if mood > 28:
            if random.randint(0,10) > 5:
                older()
            else:
                tetris()
            break_block()
        elif mood > 25:
            #play_music("a2--_--a2--_-a2----_-a5--------_")
            break_block()
            whoa()
        elif mood > 20: 
            #play_music("c2--_--e2--_--e2--_--f2--_--f2--_--g2--_--a2--_--b2----g2--_--a2--_--a2--_--b2--_--b2--_--c3----b2---_--_")
            break_block()
        impatience = random.randint(1,21)
        if impatience > 18:
            think_delay = random.randint(5, 20)
        elif impatience > 16:
            think_delay = random.randint(20, 60)
        elif impatience > 12:
            think_delay = random.randint(60, 120)
        else:
            think_delay = random.randint(120, 300)
        print('waiting '+str(think_delay))
        for i in range(think_delay):
            print(str(think_delay-i))
            time.sleep(1)

def check_mood():
    if mood < 0:
        grumble()
    if mood < -5:
        complain()
    if mood > 8:
        if random.randint(0,10) > 5:
            older()
        else:
            tetris()
        break_block()
    elif mood > 7:
        #play_music("a2--_--a2--_-a2----_-a5--------_")
        break_block()
        whoa()
    elif mood > 6: 
        #play_music("c2--_--e2--_--e2--_--f2--_--f2--_--g2--_--a2--_--b2----g2--_--a2--_--a2--_--b2--_--b2--_--c3----b2---_--_")
        break_block()
    print('energy '+str(energy))

def handle_buttons():
    global b1_pressed
    global b2_pressed
    global b3_pressed
    global b4_pressed
    
    b1_p = button_1.value()
    b2_p = button_2.value()
    b3_p = button_3.value()
    b4_p = button_4.value()
    
    break_wait = False
    
    if b1_p != b1_pressed:
        b1_pressed = b1_p
        if b1_pressed:
            break_wait = button_press(1)
    
    if b2_p != b2_pressed:
        b2_pressed = b2_p
        if b2_pressed:
            break_wait = button_press(2)
            
    if b3_p != b3_pressed:
        b3_pressed = b3_p
        if b3_pressed:
            break_wait = button_press(3)
            
    if b4_p != b4_pressed:
        b4_pressed = b4_p
        if b4_pressed:
            break_wait = button_press(4)
    
    return break_wait

def play_game():
    global playing
    global game_state
    print('playing a game')
    
    game_state = [True, True, True, True, True]
    game_state[random.randint(0,4)] = False
    
    for i in range(5):
        if game_state[i]:
            l[i+1].on()
            all_off = False
        else:
            l[i+1].off()
    
    playing = True
    while playing:
        handle_buttons()
        time.sleep(0.05)

def game_button(b):
    global playing
    global game_state
    if b == 1:
        game_state[0] = game_state[0] == False
        game_state[1] = game_state[1] == False
    if b == 2:
        game_state[1] = game_state[1] == False
        game_state[2] = game_state[2] == False
    if b == 3:
        game_state[2] = game_state[2] == False
        game_state[3] = game_state[3] == False
    if b == 4:
        game_state[3] = game_state[3] == False
        game_state[4] = game_state[4] == False
    
    all_off = True
    for i in range(5):
        if game_state[i]:
            l[i+1].on()
            all_off = False
        else:
            l[i+1].off()
    
    if all_off:
        playing = False
        tetris()


def play_match_game():
    global playing_match
    global game_state
    print('playing match game')

    playing_match = True

    setup_match_level()
    show_match_level()

    while playing_match:
        handle_buttons()
        if len(game_state["received"]) >= len(game_state["pattern"]):
            check = check_match_win()
            if check:
                break
        time.sleep(0.05)

def show_match_level():
    delay = 1 / game_state["level"]
    print(game_state["pattern"])
    if delay < 0.05:
        delay = 0.05
    for n in game_state["pattern"]:
        if n == 1:
            play_note('b3', delay)
        elif n == 2:
            play_note('f4#', delay)
        elif n == 3:
            play_note('g4#', delay)
        time.sleep(delay)

def setup_match_level():
    global game_state
    game_state["pattern"] = []
    game_state["received"] = []
    for i in range(game_state["level"]+2):
        b = random.randint(1,3)
        game_state["pattern"].append(b)

def match_game_button(b):
    global playing_match
    global game_state
    
    delay = 1 / game_state["level"]
    if delay < 0.05:
        delay = 0.05
    
    if b == 1:
        playing_match = False
        return
    n = 0
    if b == 2:
        n = 1
        play_note('b3', delay)
    elif b == 3:
        n = 2
        play_note('f4#', delay)
    elif b == 4:
        n = 3
        play_note('g4#', delay)
        
    game_state["received"].append(n)

def check_match_win():
    global playing_match
    global game_state
    for i in range(len(game_state["received"])):
        if game_state["received"][i] != game_state["pattern"][i]:
            grumble()
            playing_match = False
            think()
            return False
    time.sleep(0.5)
    triumph()
    time.sleep(1)
    game_state["level"] = game_state["level"]+1
    for i in range(game_state["level"]):
        play_note('c4',0.1)
        time.sleep(0.1)
    time.sleep(2)
    return True

def run():
    global mood
    global think_delay
    
    while True:
        think()
        print('mood '+str(mood))
        check_mood()
        if energy == 0:
            rest()
        impatience = random.randint(1,21) - mood
        if impatience > 18:
            think_delay = random.randint(5, 20)
        elif impatience > 16:
            think_delay = random.randint(20, 60)
        elif impatience > 12:
            think_delay = random.randint(60, 120)
        else:
            think_delay = random.randint(120, 300)
        print('waiting '+str(think_delay))
        think_delay = think_delay * 20
        while think_delay > 0:
            break_wait = handle_buttons()
            if playing_match:
                play_match_game()
            think_delay = think_delay - 1
            if break_wait:
                think_delay = 0
                
            time.sleep(0.05)

def triumph():
    play_note('c5',0.2)
    time.sleep(0.2)
    play_note('a4',0.05)
    time.sleep(0.05)
    play_note('b4',0.1)
    play_note('c5',0.5)

def button_press(b):
    global playing
    global playing_match
    global game_state
    if playing:
        game_button(b)
        return False
    if playing_match:
        match_game_button(b)
        return False
    print('button '+str(b))
    if b == 1:
        roll = random.randint(1,4)
        if roll == 1:
            whoa()
        elif roll == 2:
            grumble()
        elif roll == 3:
            complain()
        else:
            triumph()
    if b == 2:
        #think()
        #time.sleep(0.5)
        #check_mood()
        game_state = {
            "level": 1,
            "pattern": [],
            "received": []
        }
        play_match_game()
    if b == 3:
        play_game()
    if b == 4:
        break_block()
    return False

if __name__ == "__main__":
    run()


