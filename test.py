import json

def convertthing(thing):
    a = thing.split(', ')
    b = a[0].split('/')
    c = a[1].split(":")
    day = b[1]
    month = b[0]
    year = b[2]
    hour = c[0]
    return year+month+day+hour

def convertfile(file):
    f = open("/home/pi/"+file+"log_2021082014.txt")
    t = f.read()
    data = {}
    for l in t.split('\n'):
        if l == "":
            continue
        d = json.loads(l)
        dt = convertthing(d[0])
        data[dt].append(d)
    for k in data.keys():
        text = ""
        for line in data[k]:
            text = text + json.dumps(line) + "\n"
        with open("/home/pi/"+file+"log_"+k+".txt","w") as write_file:
            write_file.write(text)

convertfile("power")
convertfile("temp")