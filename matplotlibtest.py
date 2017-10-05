import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation


def data_gen(t=0):
    cnt = 0
    while cnt < 1000:
        cnt += 1
        t += 0.1
        yield t, 100 * np.sin(2*np.pi*t) * np.exp(-t/10.), t, 120 * np.sin(2.5*np.pi*t) * np.exp(-t/10.)

def init():
    ax.set_ylim(40, 140)# change range!
    ax.set_xlim(0, 10)
    del xdata[:]
    del ydata[:]
    del xdata2[:]
    del ydata2[:]
    line.set_data(xdata, ydata)
    line.set_data(xdata2, ydata2)
    return line, line2,

fig, ax = plt.subplots()
line, = ax.plot([], [], lw=1)
line2, = ax.plot([], [], lw=1)

ax.set_title("Pulse and SpO2 Tracker")
#ax.set_autoscaley_on(False)
text_pulse = "Pulse:"
text_spo2 = "SpO2:"
props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
ax.text(0.05, 0.95, text_pulse, transform=ax.transAxes, fontsize=14,
              color='blue', verticalalignment='top', bbox=props)
ax.text(0.05, 0.85, text_spo2, transform=ax.transAxes, fontsize=14,
              color='green', verticalalignment='top', bbox=props)

#ax.grid() # add grid
xdata, ydata = [], []
xdata2, ydata2 = [], []


def run(data):
    # update the data
    t, y, t, y2 = data
    xdata.append(t)
    ydata.append(y)
    xdata2.append(t)
    ydata2.append(y2)
    xmin, xmax = ax.get_xlim()

    if t >= xmax:
        ax.set_xlim(xmin, 2*xmax)
        ax.figure.canvas.draw()
    line.set_data(xdata, ydata)
    line2.set_data(xdata2, ydata2)

    return line, line2,

ani = animation.FuncAnimation(fig, run, data_gen, blit=False, interval=10,
                              repeat=False, init_func=init)
plt.show()
