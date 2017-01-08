##import matplotlib.pyplot as plt
##import matplotlib.animation as animation
##import time
##
##fig = plt.figure()
##ax1 = fig.add_subplot(1,1,1)
##
##def animate(i):
##    xar = [1,2,3,4,5]
##    yar = [2,4,8,16,32]
##    ax1.clear()
##    ax1.plot(xar,yar)
##ani = animation.FuncAnimation(fig, animate, interval=1000)
##plt.show()
##
##time.sleep(3)

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

fig, ax = plt.subplots()

x = np.arange(0, 2*np.pi, 0.01)
line, = ax.plot(x, np.sin(x))


def animate(i):
    line.set_ydata(np.sin(x + i/10.0))  # update the data
    return line,


# Init only required for blitting to give a clean slate.
def init():
    line.set_ydata(np.ma.array(x, mask=True))
    return line,

ani = animation.FuncAnimation(fig, animate, np.arange(1, 200), init_func=init,
                              interval=25, blit=True)
plt.show()
