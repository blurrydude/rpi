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

chars = [' ','.','_']

dit_time = 0.05
da_time = 0.15
key_wait = 0.05
space_wait = 0.5

def get_code(message):
    coded = ''
    for letter in message:
        l = letter.lower()
        if l not in morse.keys():
            coded = coded + '   '
            continue
        code = morse[l]
        for v in code:
            coded = coded + chars[v]
        coded = coded + ' '
    return coded

file = open("C:\\Users\\idkline\\Downloads\\Death In Tube Seven.txt","r")
text = file.read()
file.close()
morse_file = open("morse.txt","w")
morse_file.write(get_code(text))
morse_file.close()