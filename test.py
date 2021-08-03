import base64
from random import randint
import hashlib

pronouns = ["I","We","They"]
spronouns = ["He","She","It"]
verbs = ["love","hate","like","despise","admire","loathe","adore","tolerate","own","consume","paint","draw","sketch","build","sculpt","summon"]
adjectives = ["plastic","glass","stone","wooden","organic","regular","medium","large","small","irregular","moronic","beautiful","terrifying","regulatory"]
nouns = ["badgers","clowns","fruit","vegetables","crates","pillows","boats","pants","wheels","aardvarks","nighties","amoeba","cars","cathedrals","spoons","albums"]

def b64(message):
    message_bytes = message.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    return base64_bytes.decode('ascii')

def md5hash(message):
    message_bytes = message.encode('ascii')
    base64_bytes = hashlib.md5(message_bytes)
    return base64_bytes.hexdigest()

def gen_rand_pvan():
    s = randint(0,1)
    adds = ""
    if s == 0:
        p = pronouns[randint(0,len(pronouns)-1)]
    else:
        p = spronouns[randint(0,len(spronouns)-1)]
        adds = "s"

    v = verbs[randint(0,len(verbs)-1)]
    a = adjectives[randint(0,len(adjectives)-1)]
    n = nouns[randint(0,len(nouns)-1)]
    print(p + " " + v + adds + " " + a + " " + n)

def base64_default():
    print(b64("I hate regulatory badgers"))
    print(md5hash("I hate regulatory badgers"))
    print(md5hash(b64("I hate regulatory badgers")))

base64_default()