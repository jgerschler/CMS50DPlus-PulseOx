import matplotlib.pyplot as plt
import matplotlib.animation as animation

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)

def animate(i):
    xar = [1,2,3,4,5]
    yar = [2,4,8,16,32]
    ax1.clear()
    ax1.plot(xar,yar)
    
ani = animation.FuncAnimation(fig, animate, interval=1000)
plt.show()
