from cProfile import label
import matplotlib.pyplot as plt
import numpy as np

x = []
t = []
h = []
w = []

data = open("C:\\Users\\kline\\Dropbox\\sensor_data-20220808.log").readlines()
for i in range(0,len(data)-4):
    line = data[i]
    if len(line) < 3:
        continue
    if i%2==0:
        s = line.replace(": Temp=","|").replace("*  Humidity=","|").replace("%","").split("|")
        x.append(((i/2)*(1/6))/60)
        t.append(float(s[1]))
        h.append(float(s[2]))
    else:
        s = line.split(": ")
        w.append(float(s[1]))

fig, ax = plt.subplots()
ax.plot(x, h, label="Relative Humidity (%) ")
ax.plot(x, t, label="Temperature (F) ")
ax.plot(x, w, label="Water (ml) ")
ax.set_xlabel("Hours")
ax.legend()
plt.show()