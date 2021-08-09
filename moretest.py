import requests

def convert_suntime(jdata, winter):
    a = jdata.split(' ')
    s = a[0].split(":")
    h = int(s[0])
    if a[1] == "AM" and h == 12:
        h = 0
    if a[1] == "PM" and h != 12:
        h = h + 12
    if winter is True:
        h = h - 5
    else:
        h = h - 4
    if h < 0:
        h = h + 24
    if h == 24:
        h = 0
    m = int(s[1])
    o = ""
    if h < 10:
        o = "0"
    o = o + str(h) + ":"
    if m < 10:
        o = o + "0"
    o = o + str(m)
    return o
r = requests.get("https://api.sunrise-sunset.org/json?lat=39.68021508778703&lng=-84.17636552954109")
j = r.json()

terms = [
    "sunrise",
    "sunset",
    "civil_twilight_begin",
    "civil_twilight_end"
]
for term in terms:
    print(term+": "+convert_suntime(j["results"][term],False))