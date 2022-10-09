from cProfile import label
import matplotlib.pyplot as plt
import numpy as np

x = []
t = []
h = []
w = []
d = []

data = open("C:\\Users\\idkline\\Dropbox\\sensor_data_summary-final.log").readlines()
min = 0
for i in range(0,len(data)-2):
    line = data[i]
    if len(line) < 3:
        continue

    s = line.split("|")
    #x.append(((i/2)*(1/6))/60)
    x.append(float(s[0]))
    t.append(float(s[1]))
    h.append(float(s[2]))
    # if min == 0:
    #     min = float(s[3]) * -1 
    # w.append((float(s[3])+min)*1.1)
    w.append((float(s[3]))*1.1)
    #d.append(float(s[4])*10)

fig, ax = plt.subplots()
ax.plot(x, h, label="Relative Humidity (%) ")
ax.plot(x, t, label="Temperature (F) ")
ax.plot(x, w, label="Water (ml) ")
#ax.plot(x, d, label="Diff ")
ax.set_xlabel("Hours")
ax.legend()
plt.show()