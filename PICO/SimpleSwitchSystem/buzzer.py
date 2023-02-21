from machine import Pin, PWM
import time

class Buzzer:
    def __init__(self, pwm_pin):
        self.buzzer = PWM(Pin(pwm_pin))
        self.current_note = ''
        self.notes = [
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

    def note(self, n):
        #print('note:'+n)
        ni = self.note_index(n)
        #print('note index:'+str(ni))
        return self.notes[ni]

    def note_index(self, n):
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
        
    def play_note(self, n, dur):
        #print('play note:'+n)
        f = self.note(n)
        #print('note freq:'+str(f))
        self.play_tone(f)
        time.sleep(dur)
        self.be_quiet()
        
    def play_note_id(self, i, dur):
        self.play_tone(self.notes[i])
        time.sleep(dur)
        self.be_quiet()

    def play_tone(self, frequency):
        # Set maximum volume
        self.buzzer.duty_u16(1000)
        # Play tone
        self.buzzer.freq(round(frequency))

    def be_quiet(self):
        # Set minimum volume
        self.buzzer.duty_u16(0)

    def play_music(self, music):
        beat = 0.1
        self.current_note = ''
        start_note = True
        sustain = True
        for c in music:
            try:
                #print(c)
                if c == '-' and start_note is True:
                    #print('play_tone '+current_note)
                    self.play_tone(self.note(self.current_note))
                    start_note = False
                    sustain = True
                elif c == '-' and start_note is False:
                    #print('beat')
                    time.sleep(beat)
                elif c == '_':
                    #print('be_quiet')
                    self.be_quiet()
                    start_note = False
                elif sustain is True:
                    sustain = False
                    #print('stop_note')
                    self.current_note = ''
                    #print('build current_note')
                    self.current_note = self.current_note + c
                else:
                    #print('build current_note')
                    self.current_note = self.current_note + c
                    start_note = True
            except:
                print('bad at '+c)
                self.be_quiet()
        self.be_quiet()

