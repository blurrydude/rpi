from random import randint

pronouns = ["I","We","They"]
spronouns = ["He","She","It"]
verbs = ["love","hate","like","despise","admire","loathe","adore","tolerate","own","consume","paint","draw","sketch","build","sculpt","summon"]
adjectives = ["plastic","glass","stone","wooden","organic","regular","medium","large","small","irregular","moronic","beautiful","terrifying","regulatory"]
nouns = ["badgers","clowns","fruit","vegetables","crates","pillows","boats","pants","wheels","aardvarks","nighties","amoeba","cars","cathedrals","spoons","albums"]

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

for i in range(15):
    gen_rand_pvan()